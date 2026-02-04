"""
Service Layer for Inventory Management System.

This module contains business logic services that orchestrate operations across
multiple models and provide a clean interface for views to interact with the
domain logic. Following the service layer pattern keeps views thin and makes
business logic more testable and reusable.

Services are organized by domain area:
- BranchService: Branch/filial management operations
- DepartmentService: Department operations
- EmployeeService: Employee management operations
- EquipmentService: Equipment management operations
- AssignmentService: Equipment assignment workflow
- MaintenanceService: Maintenance scheduling and tracking
- InventoryCheckService: Inventory verification operations
- AuditService: Audit logging operations
- OTPService: OTP generation and verification
- ExportService: Data export operations
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, QuerySet, Count, Sum, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Branch, Department, Employee, EquipmentCategory, Equipment,
    Assignment, MaintenanceRecord, InventoryCheck, AuditLog,
    PasswordChangeOTP
)
from .constants import (
    EquipmentStatus, MaintenanceStatus, AuditAction,
    ErrorMessages, SuccessMessages
)
from .utils import (
    calculate_depreciation,
    is_warranty_active,
    generate_equipment_qr_url,
    generate_employee_qr_url,
    generate_otp_code,
    get_otp_expiry_time
)


# ============================================
# Branch Service
# ============================================

class BranchService:
    """
    Service for branch/filial-related operations.

    Handles branch creation, hierarchy management, statistics calculation,
    and queries. Provides methods for managing multi-location organizational structure.

    Examples:
        >>> service = BranchService()
        >>> branch = service.create_branch(data, user)
        >>> stats = service.get_branch_statistics(branch)
        >>> hierarchy = service.get_branch_hierarchy(branch)
    """

    @staticmethod
    def create_branch(
        data: Dict[str, Any],
        user: Optional[User] = None
    ) -> Branch:
        """
        Create new branch with proper initialization.

        Args:
            data: Branch data dictionary
            user: User creating the branch

        Returns:
            Created Branch instance

        Raises:
            ValidationError: If data is invalid or creates circular reference

        Examples:
            >>> data = {
            ...     'code': 'HQ001',
            ...     'name': 'Bosh ofis',
            ...     'branch_type': 'HEADQUARTERS',
            ...     'address': 'Toshkent sh., ...',
            ...     'city': 'Toshkent'
            ... }
            >>> branch = BranchService.create_branch(data, request.user)
        """
        with transaction.atomic():
            # Validate parent branch doesn't create circular reference
            parent_branch = data.get('parent_branch')
            if parent_branch:
                if parent_branch.parent_branch and parent_branch.parent_branch.id in data:
                    raise ValidationError("Davriy havola yaratish mumkin emas")

            branch = Branch.objects.create(
                **data,
                created_by=user,
                last_modified_by=user
            )

            # Log action
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user=user,
                obj=branch,
                description=f"Yangi filial yaratildi: {branch.name}"
            )

            return branch

    @staticmethod
    def update_branch(
        branch: Branch,
        data: Dict[str, Any],
        user: Optional[User] = None
    ) -> Branch:
        """
        Update branch with validation and audit logging.

        Args:
            branch: Branch instance to update
            data: Updated data
            user: User performing the update

        Returns:
            Updated Branch instance

        Raises:
            ValidationError: If update creates circular reference

        Examples:
            >>> data = {'name': 'Yangi nom', 'phone': '+998901234567'}
            >>> branch = BranchService.update_branch(branch, data, request.user)
        """
        with transaction.atomic():
            # Validate parent branch change doesn't create circular reference
            if 'parent_branch' in data:
                new_parent = data['parent_branch']
                if new_parent:
                    # Check if new parent is self
                    if new_parent.id == branch.id:
                        raise ValidationError("Filial o'zini ota-filial qilib belgilay olmaydi")

                    # Check if new parent is a sub-branch of this branch
                    all_sub_branches = branch.get_all_sub_branches()
                    if new_parent in all_sub_branches:
                        raise ValidationError("Quyi filialni ota-filial qilib belgilab bo'lmaydi")

            # Update fields
            for field, value in data.items():
                setattr(branch, field, value)

            branch.last_modified_by = user
            branch.save()

            # Log action
            AuditLog.log_action(
                action=AuditAction.UPDATE,
                user=user,
                obj=branch,
                description=f"Filial ma'lumotlari yangilandi: {branch.name}"
            )

            return branch

    @staticmethod
    def get_branch_statistics(branch: Branch) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a branch.

        Args:
            branch: Branch instance

        Returns:
            Dictionary with branch statistics

        Examples:
            >>> stats = BranchService.get_branch_statistics(branch)
            >>> print(stats['total_employees'])
            25
        """
        return {
            'branch_id': branch.id,
            'branch_name': branch.name,
            'branch_type': branch.get_branch_type_display(),

            # Employee statistics
            'total_employees': branch.get_employee_count(),
            'active_employees': branch.employees.filter(is_active=True).count(),
            'inactive_employees': branch.employees.filter(is_active=False).count(),

            # Department statistics
            'total_departments': branch.departments.filter(is_active=True).count(),
            'departments_with_managers': branch.departments.filter(
                is_active=True,
                manager__isnull=False
            ).count(),

            # Equipment statistics
            'total_equipment': branch.get_equipment_count(),
            'available_equipment': branch.equipments.filter(
                is_active=True,
                status=EquipmentStatus.AVAILABLE
            ).count(),
            'assigned_equipment': branch.equipments.filter(
                is_active=True,
                status=EquipmentStatus.ASSIGNED
            ).count(),
            'maintenance_equipment': branch.equipments.filter(
                is_active=True,
                status=EquipmentStatus.MAINTENANCE
            ).count(),

            # Hierarchy statistics
            'direct_sub_branches': branch.sub_branches.filter(is_active=True).count(),
            'total_sub_branches': len(branch.get_all_sub_branches()),
            'hierarchy_level': branch.get_hierarchy_level(),

            # Status
            'is_operational': branch.is_operational(),
            'is_active': branch.is_active
        }

    @staticmethod
    def get_branch_hierarchy(branch: Branch) -> Dict[str, Any]:
        """
        Get hierarchical structure of branch and its sub-branches.

        Args:
            branch: Root branch instance

        Returns:
            Nested dictionary representing hierarchy

        Examples:
            >>> hierarchy = BranchService.get_branch_hierarchy(branch)
            >>> print(hierarchy['children'])
        """
        def build_tree(b: Branch) -> Dict[str, Any]:
            return {
                'id': b.id,
                'code': b.code,
                'name': b.name,
                'branch_type': b.get_branch_type_display(),
                'city': b.city,
                'is_active': b.is_active,
                'employee_count': b.get_employee_count(),
                'equipment_count': b.get_equipment_count(),
                'children': [
                    build_tree(child)
                    for child in b.sub_branches.filter(is_active=True).order_by('name')
                ]
            }

        return build_tree(branch)

    @staticmethod
    def get_all_branches_hierarchy() -> List[Dict[str, Any]]:
        """
        Get complete hierarchy of all branches starting from root branches.

        Returns:
            List of hierarchical dictionaries for root branches

        Examples:
            >>> hierarchies = BranchService.get_all_branches_hierarchy()
            >>> for root in hierarchies:
            ...     print(root['name'])
        """
        root_branches = Branch.objects.filter(
            parent_branch__isnull=True,
            is_active=True
        ).order_by('name')

        return [
            BranchService.get_branch_hierarchy(branch)
            for branch in root_branches
        ]

    @staticmethod
    def search_branches(
        query: str = None,
        branch_type: str = None,
        city: str = None,
        is_active: bool = True
    ) -> QuerySet:
        """
        Search branches with various filters.

        Args:
            query: Search term for code/name
            branch_type: Filter by branch type
            city: Filter by city
            is_active: Filter by active status

        Returns:
            QuerySet of matching branches

        Examples:
            >>> branches = BranchService.search_branches(
            ...     query='toshkent',
            ...     branch_type='REGIONAL'
            ... )
        """
        queryset = Branch.objects.all()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) |
                Q(name__icontains=query) |
                Q(address__icontains=query)
            )

        if branch_type:
            queryset = queryset.filter(branch_type=branch_type)

        if city:
            queryset = queryset.filter(city__icontains=city)

        return queryset.order_by('name')

    @staticmethod
    def deactivate_branch(
        branch: Branch,
        user: Optional[User] = None,
        cascade: bool = False
    ) -> None:
        """
        Deactivate a branch and optionally its sub-branches.

        Args:
            branch: Branch to deactivate
            user: User performing the action
            cascade: If True, deactivate all sub-branches as well

        Examples:
            >>> BranchService.deactivate_branch(branch, request.user, cascade=True)
        """
        with transaction.atomic():
            branch.deactivate()
            branch.last_modified_by = user
            branch.save()

            if cascade:
                for sub_branch in branch.get_all_sub_branches():
                    sub_branch.deactivate()
                    sub_branch.last_modified_by = user
                    sub_branch.save()

            # Log action
            AuditLog.log_action(
                action=AuditAction.UPDATE,
                user=user,
                obj=branch,
                description=f"Filial nofaollashtirildi: {branch.name}" +
                           (" (barcha quyi filiallar bilan)" if cascade else "")
            )

    @staticmethod
    def get_branch_employees_by_department(branch: Branch) -> Dict[str, List[Employee]]:
        """
        Get all employees in a branch grouped by department.

        Args:
            branch: Branch instance

        Returns:
            Dictionary mapping department names to employee lists

        Examples:
            >>> employees_by_dept = BranchService.get_branch_employees_by_department(branch)
            >>> for dept, emps in employees_by_dept.items():
            ...     print(f"{dept}: {len(emps)} employees")
        """
        employees = branch.employees.filter(is_active=True).select_related('department')
        result = {}

        for employee in employees:
            dept_name = employee.department.name if employee.department else "Bo'limsiz"
            if dept_name not in result:
                result[dept_name] = []
            result[dept_name].append(employee)

        return result


# ============================================
# Equipment Service
# ============================================

class EquipmentService:
    """
    Service for equipment-related operations.

    Handles equipment creation, updates, status changes, and queries.
    Provides methods for complex equipment operations that involve
    multiple models or business rules.

    Examples:
        >>> service = EquipmentService()
        >>> equipment = service.create_equipment(data, user)
        >>> service.update_status(equipment, EquipmentStatus.MAINTENANCE, user)
    """

    @staticmethod
    def create_equipment(
        data: Dict[str, Any],
        user: Optional[User] = None,
        generate_qr: bool = True
    ) -> Equipment:
        """
        Create new equipment with proper initialization.

        Args:
            data: Equipment data dictionary
            user: User creating the equipment
            generate_qr: Whether to generate QR code automatically

        Returns:
            Created Equipment instance

        Raises:
            ValidationError: If data is invalid

        Examples:
            >>> data = {
            ...     'name': 'Laptop',
            ...     'inventory_number': 'INV001',
            ...     'category': category_obj,
            ...     'purchase_price': 1000.00
            ... }
            >>> equipment = EquipmentService.create_equipment(data, request.user)
        """
        with transaction.atomic():
            equipment = Equipment.objects.create(
                **data,
                created_by=user,
                last_modified_by=user
            )

            # Calculate initial current value
            equipment.calculate_current_value()
            equipment.save()

            # Generate QR code if requested
            if generate_qr:
                equipment.generate_qr_code()
                equipment.save()

            # Log the creation
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user=user,
                obj=equipment,
                description=f"Created equipment: {equipment.name}"
            )

            return equipment

    @staticmethod
    def update_equipment(
        equipment: Equipment,
        data: Dict[str, Any],
        user: Optional[User] = None
    ) -> Equipment:
        """
        Update equipment with change tracking.

        Args:
            equipment: Equipment instance to update
            data: Updated data dictionary
            user: User performing the update

        Returns:
            Updated Equipment instance

        Examples:
            >>> EquipmentService.update_equipment(
            ...     equipment,
            ...     {'status': EquipmentStatus.MAINTENANCE},
            ...     request.user
            ... )
        """
        with transaction.atomic():
            # Track changes for audit
            old_values = {
                field: getattr(equipment, field)
                for field in data.keys()
                if hasattr(equipment, field)
            }

            # Update fields
            for field, value in data.items():
                setattr(equipment, field, value)

            equipment.last_modified_by = user

            # Recalculate value if financial fields changed
            if any(field in data for field in ['purchase_price', 'depreciation_rate']):
                equipment.calculate_current_value()

            equipment.save()

            # Log the update
            changes = []
            for field, old_value in old_values.items():
                new_value = data[field]
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} → {new_value}")

            if changes:
                AuditLog.log_action(
                    action=AuditAction.UPDATE,
                    user=user,
                    obj=equipment,
                    description=f"Updated equipment: {', '.join(changes)}"
                )

            return equipment

    @staticmethod
    def update_status(
        equipment: Equipment,
        new_status: str,
        user: Optional[User] = None,
        reason: Optional[str] = None
    ) -> Equipment:
        """
        Update equipment status with validation and logging.

        Args:
            equipment: Equipment instance
            new_status: New status value
            user: User performing the status change
            reason: Optional reason for status change

        Returns:
            Updated Equipment instance

        Raises:
            ValidationError: If status transition is invalid

        Examples:
            >>> EquipmentService.update_status(
            ...     equipment,
            ...     EquipmentStatus.MAINTENANCE,
            ...     request.user,
            ...     "Scheduled maintenance"
            ... )
        """
        old_status = equipment.status

        # Validate status transition
        if old_status == new_status:
            return equipment

        with transaction.atomic():
            equipment.status = new_status
            equipment.last_modified_by = user
            equipment.save()

            # Log status change
            description = f"Status changed: {old_status} → {new_status}"
            if reason:
                description += f" (Reason: {reason})"

            AuditLog.log_action(
                action=AuditAction.UPDATE,
                user=user,
                obj=equipment,
                description=description
            )

            return equipment

    @staticmethod
    def get_available_equipment(
        category: Optional[EquipmentCategory] = None,
        only_active: bool = True
    ) -> QuerySet:
        """
        Get queryset of available equipment.

        Args:
            category: Optional category filter
            only_active: Filter for active equipment only

        Returns:
            QuerySet of available equipment

        Examples:
            >>> equipment_list = EquipmentService.get_available_equipment(
            ...     category=laptop_category
            ... )
        """
        queryset = Equipment.objects.filter(status=EquipmentStatus.AVAILABLE)

        if only_active:
            queryset = queryset.filter(is_active=True)

        if category:
            queryset = queryset.filter(category=category)

        return queryset.select_related('category').order_by('name')

    @staticmethod
    def get_equipment_by_status(status: str) -> QuerySet:
        """
        Get equipment filtered by status.

        Args:
            status: Equipment status to filter by

        Returns:
            QuerySet of equipment

        Examples:
            >>> maintenance_equipment = EquipmentService.get_equipment_by_status(
            ...     EquipmentStatus.MAINTENANCE
            ... )
        """
        return Equipment.objects.filter(
            status=status,
            is_active=True
        ).select_related('category').order_by('-updated_at')

    @staticmethod
    def search_equipment(query: str) -> QuerySet:
        """
        Search equipment by multiple fields.

        Args:
            query: Search query string

        Returns:
            QuerySet of matching equipment

        Examples:
            >>> results = EquipmentService.search_equipment("laptop")
        """
        return Equipment.objects.filter(
            Q(name__icontains=query) |
            Q(inventory_number__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(model__icontains=query)
        ).select_related('category').distinct()

    @staticmethod
    def calculate_total_value(
        category: Optional[EquipmentCategory] = None,
        status: Optional[str] = None
    ) -> Decimal:
        """
        Calculate total current value of equipment.

        Args:
            category: Optional category filter
            status: Optional status filter

        Returns:
            Total current value as Decimal

        Examples:
            >>> total = EquipmentService.calculate_total_value(
            ...     status=EquipmentStatus.AVAILABLE
            ... )
        """
        queryset = Equipment.objects.filter(is_active=True)

        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)

        result = queryset.aggregate(total=Sum('current_value'))
        return result['total'] or Decimal('0.00')


# ============================================
# Assignment Service
# ============================================

class AssignmentService:
    """
    Service for equipment assignment operations.

    Handles assignment workflow including creation, approval, return,
    and validation of business rules around assignments.

    Examples:
        >>> service = AssignmentService()
        >>> assignment = service.assign_equipment(equipment, employee, user)
        >>> service.return_equipment(assignment, user)
    """

    @staticmethod
    def assign_equipment(
        equipment: Equipment,
        employee: Employee,
        user: Optional[User] = None,
        assigned_by: Optional[Employee] = None,
        notes: Optional[str] = None,
        expected_return_date: Optional[date] = None
    ) -> Assignment:
        """
        Assign equipment to an employee.

        Args:
            equipment: Equipment to assign
            employee: Employee receiving the equipment
            user: User performing the assignment
            assigned_by: Employee performing the assignment
            notes: Optional assignment notes
            expected_return_date: Expected return date

        Returns:
            Created Assignment instance

        Raises:
            ValidationError: If equipment cannot be assigned

        Examples:
            >>> assignment = AssignmentService.assign_equipment(
            ...     equipment=laptop,
            ...     employee=john_doe,
            ...     user=request.user,
            ...     notes="For project work"
            ... )
        """
        # Validate equipment can be assigned
        if equipment.status != EquipmentStatus.AVAILABLE:
            raise ValidationError(
                ErrorMessages.EQUIPMENT_NOT_AVAILABLE.format(status=equipment.status)
            )

        # Check for existing active assignment
        existing = Assignment.objects.filter(
            equipment=equipment,
            return_date__isnull=True
        ).first()

        if existing:
            raise ValidationError(ErrorMessages.EQUIPMENT_ALREADY_ASSIGNED)

        with transaction.atomic():
            # Create assignment
            assignment = Assignment.objects.create(
                equipment=equipment,
                employee=employee,
                assigned_by=user,
                expected_return_date=expected_return_date,
                notes=notes
            )

            # Update equipment status
            equipment.status = EquipmentStatus.ASSIGNED
            equipment.last_modified_by = user
            equipment.save()

            # Log the assignment
            AuditLog.log_action(
                action=AuditAction.ASSIGN,
                user=user,
                obj=equipment,
                description=f"Assigned to {employee.get_full_name()}"
            )

            return assignment

    @staticmethod
    def return_equipment(
        assignment: Assignment,
        user: Optional[User] = None,
        returned_by: Optional[Employee] = None,
        condition: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Assignment:
        """
        Process equipment return.

        Args:
            assignment: Assignment to return
            user: User processing the return
            returned_by: Employee returning the equipment
            condition: Equipment condition on return
            notes: Optional return notes

        Returns:
            Updated Assignment instance

        Raises:
            ValidationError: If equipment already returned

        Examples:
            >>> AssignmentService.return_equipment(
            ...     assignment=assignment,
            ...     user=request.user,
            ...     condition=EquipmentCondition.GOOD
            ... )
        """
        if assignment.return_date:
            raise ValidationError("Equipment already returned")

        with transaction.atomic():
            # Update assignment
            assignment.return_date = timezone.now()
            assignment.returned_by = user
            assignment.condition_on_return = condition
            if notes:
                assignment.return_notes = notes
            assignment.save()

            # Update equipment status
            equipment = assignment.equipment
            equipment.status = EquipmentStatus.AVAILABLE
            if condition:
                equipment.condition = condition
            equipment.last_modified_by = user
            equipment.save()

            # Log the return
            AuditLog.log_action(
                action=AuditAction.RETURN,
                user=user,
                obj=equipment,
                description=f"Returned by {assignment.employee.get_full_name()}"
            )

            return assignment

    @staticmethod
    def get_active_assignments(
        employee: Optional[Employee] = None,
        equipment: Optional[Equipment] = None
    ) -> QuerySet:
        """
        Get active (not returned) assignments.

        Args:
            employee: Optional employee filter
            equipment: Optional equipment filter

        Returns:
            QuerySet of active assignments

        Examples:
            >>> assignments = AssignmentService.get_active_assignments(
            ...     employee=john_doe
            ... )
        """
        queryset = Assignment.objects.filter(return_date__isnull=True)

        if employee:
            queryset = queryset.filter(employee=employee)
        if equipment:
            queryset = queryset.filter(equipment=equipment)

        return queryset.select_related('equipment', 'employee', 'assigned_by')

    @staticmethod
    def get_overdue_assignments() -> QuerySet:
        """
        Get assignments that are overdue for return.

        Returns:
            QuerySet of overdue assignments

        Examples:
            >>> overdue = AssignmentService.get_overdue_assignments()
        """
        today = date.today()
        return Assignment.objects.filter(
            return_date__isnull=True,
            expected_return_date__lt=today
        ).select_related('equipment', 'employee')

    @staticmethod
    def get_employee_assignment_history(employee: Employee) -> QuerySet:
        """
        Get complete assignment history for an employee.

        Args:
            employee: Employee instance

        Returns:
            QuerySet of assignments

        Examples:
            >>> history = AssignmentService.get_employee_assignment_history(john_doe)
        """
        return Assignment.objects.filter(
            employee=employee
        ).select_related('equipment', 'assigned_by', 'returned_by').order_by('-assigned_date')


# ============================================
# Maintenance Service
# ============================================

class MaintenanceService:
    """
    Service for maintenance operations.

    Handles maintenance record creation, scheduling, completion tracking,
    and maintenance history queries.

    Examples:
        >>> service = MaintenanceService()
        >>> record = service.schedule_maintenance(equipment, date.today(), user)
        >>> service.complete_maintenance(record, user)
    """

    @staticmethod
    def schedule_maintenance(
        equipment: Equipment,
        scheduled_date: date,
        maintenance_type: str,
        description: str,
        priority: str,
        user: Optional[User] = None,
        assigned_to: Optional[Employee] = None,
        estimated_cost: Optional[Decimal] = None
    ) -> MaintenanceRecord:
        """
        Schedule maintenance for equipment.

        Args:
            equipment: Equipment to maintain
            scheduled_date: Date scheduled for maintenance
            maintenance_type: Type of maintenance
            description: Maintenance description
            priority: Priority level
            user: User scheduling maintenance
            assigned_to: Employee assigned to perform maintenance
            estimated_cost: Estimated cost

        Returns:
            Created MaintenanceRecord instance

        Examples:
            >>> record = MaintenanceService.schedule_maintenance(
            ...     equipment=laptop,
            ...     scheduled_date=date.today() + timedelta(days=7),
            ...     maintenance_type=MaintenanceType.INSPECTION,
            ...     description="Regular inspection",
            ...     priority=MaintenancePriority.MEDIUM,
            ...     user=request.user
            ... )
        """
        with transaction.atomic():
            record = MaintenanceRecord.objects.create(
                equipment=equipment,
                maintenance_type=maintenance_type,
                scheduled_date=scheduled_date,
                description=description,
                priority=priority,
                technician=assigned_to,
                performed_by=assigned_to.get_full_name() if assigned_to else '',
                estimated_cost=estimated_cost or Decimal('0.00'),
                status=MaintenanceStatus.SCHEDULED,
                created_by=user
            )

            # Update equipment status if urgent
            if priority == 'CRITICAL':
                equipment.status = EquipmentStatus.MAINTENANCE
                equipment.save()

            # Log maintenance scheduling
            AuditLog.log_action(
                action=AuditAction.MAINTAIN,
                user=user,
                obj=equipment,
                description=f"Maintenance scheduled: {maintenance_type}"
            )

            return record

    @staticmethod
    def start_maintenance(
        record: MaintenanceRecord,
        user: Optional[User] = None
    ) -> MaintenanceRecord:
        """
        Mark maintenance as started.

        Args:
            record: Maintenance record
            user: User starting the maintenance

        Returns:
            Updated MaintenanceRecord instance

        Examples:
            >>> MaintenanceService.start_maintenance(record, request.user)
        """
        with transaction.atomic():
            record.status = MaintenanceStatus.IN_PROGRESS
            record.started_date = timezone.now()
            record.save()

            # Update equipment status
            equipment = record.equipment
            equipment.status = EquipmentStatus.MAINTENANCE
            equipment.last_modified_by = user
            equipment.save()

            return record

    @staticmethod
    def complete_maintenance(
        record: MaintenanceRecord,
        user: Optional[User] = None,
        actual_cost: Optional[Decimal] = None,
        parts_cost: Optional[Decimal] = None,
        labor_cost: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> MaintenanceRecord:
        """
        Complete maintenance record.

        Args:
            record: Maintenance record to complete
            user: User completing the maintenance
            actual_cost: Actual total cost
            parts_cost: Cost of parts
            labor_cost: Cost of labor
            notes: Completion notes

        Returns:
            Updated MaintenanceRecord instance

        Examples:
            >>> MaintenanceService.complete_maintenance(
            ...     record=record,
            ...     user=request.user,
            ...     actual_cost=Decimal('150.00'),
            ...     notes="Replaced battery"
            ... )
        """
        with transaction.atomic():
            record.status = MaintenanceStatus.COMPLETED
            record.performed_date = timezone.now()

            if actual_cost is not None:
                record.actual_cost = actual_cost
            if parts_cost is not None:
                record.parts_cost = parts_cost
            if labor_cost is not None:
                record.labor_cost = labor_cost
            if notes:
                record.notes = notes

            record.save()

            # Return equipment to available if maintenance completed successfully
            equipment = record.equipment
            if equipment.status == EquipmentStatus.MAINTENANCE:
                equipment.status = EquipmentStatus.AVAILABLE
                equipment.last_modified_by = user
                equipment.save()

            # Log completion
            AuditLog.log_action(
                action=AuditAction.MAINTAIN,
                user=user,
                obj=equipment,
                description=f"Maintenance completed: {record.maintenance_type}"
            )

            return record

    @staticmethod
    def get_scheduled_maintenance(
        equipment: Optional[Equipment] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> QuerySet:
        """
        Get scheduled maintenance records.

        Args:
            equipment: Optional equipment filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            QuerySet of scheduled maintenance

        Examples:
            >>> upcoming = MaintenanceService.get_scheduled_maintenance(
            ...     start_date=date.today(),
            ...     end_date=date.today() + timedelta(days=30)
            ... )
        """
        queryset = MaintenanceRecord.objects.filter(
            status=MaintenanceStatus.SCHEDULED
        )

        if equipment:
            queryset = queryset.filter(equipment=equipment)
        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)

        return queryset.select_related('equipment', 'technician').order_by('scheduled_date')

    @staticmethod
    def get_equipment_maintenance_history(equipment: Equipment) -> QuerySet:
        """
        Get maintenance history for equipment.

        Args:
            equipment: Equipment instance

        Returns:
            QuerySet of maintenance records

        Examples:
            >>> history = MaintenanceService.get_equipment_maintenance_history(laptop)
        """
        return MaintenanceRecord.objects.filter(
            equipment=equipment
        ).select_related('technician').order_by('-scheduled_date')

    @staticmethod
    def calculate_maintenance_cost(
        equipment: Optional[Equipment] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate total maintenance costs.

        Args:
            equipment: Optional equipment filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary with cost breakdown

        Examples:
            >>> costs = MaintenanceService.calculate_maintenance_cost(
            ...     start_date=date(2024, 1, 1),
            ...     end_date=date(2024, 12, 31)
            ... )
        """
        queryset = MaintenanceRecord.objects.filter(
            status=MaintenanceStatus.COMPLETED
        )

        if equipment:
            queryset = queryset.filter(equipment=equipment)
        if start_date:
            queryset = queryset.filter(performed_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(performed_date__lte=end_date)

        totals = queryset.aggregate(
            total_cost=Sum('actual_cost'),
            parts_cost=Sum('parts_cost'),
            labor_cost=Sum('labor_cost')
        )

        return {
            'total_cost': totals['total_cost'] or Decimal('0.00'),
            'parts_cost': totals['parts_cost'] or Decimal('0.00'),
            'labor_cost': totals['labor_cost'] or Decimal('0.00'),
        }


# ============================================
# Inventory Check Service
# ============================================

class InventoryCheckService:
    """
    Service for inventory check operations.

    Handles creation and management of inventory verification checks.

    Examples:
        >>> service = InventoryCheckService()
        >>> check = service.create_check(equipment, user)
        >>> service.confirm_check(check, employee, user)
    """

    @staticmethod
    def create_check(
        equipment: Equipment,
        check_type: str,
        user: Optional[User] = None,
        notes: Optional[str] = None,
        **kwargs
    ) -> InventoryCheck:
        """
        Create inventory check record.

        Args:
            equipment: Equipment being checked
            check_type: Type of check
            user: User creating the check
            performed_by: Employee performing the check
            notes: Optional notes

        Returns:
            Created InventoryCheck instance

        Examples:
            >>> check = InventoryCheckService.create_check(
            ...     equipment=laptop,
            ...     check_type=CheckType.SCHEDULED,
            ...     user=request.user,
            ...     performed_by=inspector
            ... )
        """
        with transaction.atomic():
            check = InventoryCheck.objects.create(
                equipment=equipment,
                check_type=check_type,
                checked_by=user,
                notes=notes,
                location=kwargs.get('location', ''),
                condition=kwargs.get('condition', ''),
                is_functional=kwargs.get('is_functional', True),
            )

            # Log the check
            AuditLog.log_action(
                action=AuditAction.CHECK,
                user=user,
                obj=equipment,
                description=f"Inventory check performed: {check_type}"
            )

            return check

    @staticmethod
    def confirm_check(
        check: InventoryCheck,
        employee: Employee,
        user: Optional[User] = None
    ) -> InventoryCheck:
        """
        Employee confirmation of inventory check.

        Args:
            check: InventoryCheck instance
            employee: Employee confirming
            user: User processing confirmation

        Returns:
            Updated InventoryCheck instance

        Examples:
            >>> InventoryCheckService.confirm_check(check, john_doe, request.user)
        """
        check.employee = employee
        check.employee_confirmed = True
        check.confirmation_date = timezone.now()
        check.save()

        return check

    @staticmethod
    def get_recent_checks(
        equipment: Optional[Equipment] = None,
        days: int = 30
    ) -> QuerySet:
        """
        Get recent inventory checks.

        Args:
            equipment: Optional equipment filter
            days: Number of days to look back

        Returns:
            QuerySet of recent checks

        Examples:
            >>> recent = InventoryCheckService.get_recent_checks(days=7)
        """
        cutoff_date = date.today() - timedelta(days=days)
        queryset = InventoryCheck.objects.filter(check_date__gte=cutoff_date)

        if equipment:
            queryset = queryset.filter(equipment=equipment)

        return queryset.select_related('equipment', 'checked_by', 'employee').order_by('-check_date')


# ============================================
# Employee Service
# ============================================

class EmployeeService:
    """
    Service for employee operations.

    Handles employee management and queries.

    Examples:
        >>> service = EmployeeService()
        >>> employee = service.create_employee(data, user)
    """

    @staticmethod
    def create_employee(
        data: Dict[str, Any],
        user: Optional[User] = None,
        generate_qr: bool = True
    ) -> Employee:
        """
        Create new employee with QR code generation.

        Args:
            data: Employee data dictionary
            user: User creating the employee
            generate_qr: Whether to generate QR code

        Returns:
            Created Employee instance

        Examples:
            >>> data = {
            ...     'employee_id': 'EMP001',
            ...     'first_name': 'John',
            ...     'last_name': 'Doe',
            ...     'department': dept_obj
            ... }
            >>> employee = EmployeeService.create_employee(data, request.user)
        """
        with transaction.atomic():
            employee = Employee.objects.create(
                **data,
                created_by=user,
                last_modified_by=user
            )

            # Generate QR code if requested
            if generate_qr:
                employee.generate_qr_code()
                employee.save()

            # Log creation
            AuditLog.log_action(
                action=AuditAction.CREATE,
                user=user,
                obj=employee,
                description=f"Created employee: {employee.get_full_name()}"
            )

            return employee

    @staticmethod
    def get_active_employees(department: Optional[Department] = None) -> QuerySet:
        """
        Get active employees.

        Args:
            department: Optional department filter

        Returns:
            QuerySet of active employees

        Examples:
            >>> employees = EmployeeService.get_active_employees(it_dept)
        """
        queryset = Employee.objects.filter(is_active=True)

        if department:
            queryset = queryset.filter(department=department)

        return queryset.select_related('department').order_by('last_name', 'first_name')

    @staticmethod
    def search_employees(query: str) -> QuerySet:
        """
        Search employees by name, ID, or email.

        Args:
            query: Search query string

        Returns:
            QuerySet of matching employees

        Examples:
            >>> results = EmployeeService.search_employees("john")
        """
        return Employee.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(email__icontains=query)
        ).select_related('department').distinct()


# ============================================
# Department Service
# ============================================

class DepartmentService:
    """
    Service for department operations.

    Examples:
        >>> service = DepartmentService()
        >>> stats = service.get_department_statistics(dept)
    """

    @staticmethod
    def get_department_statistics(department: Department) -> Dict[str, Any]:
        """
        Get comprehensive department statistics.

        Args:
            department: Department instance

        Returns:
            Dictionary with statistics

        Examples:
            >>> stats = DepartmentService.get_department_statistics(it_dept)
            >>> print(stats['employee_count'])
        """
        employees = Employee.objects.filter(
            department=department,
            is_active=True
        )

        assigned_equipment = Equipment.objects.filter(
            assignment__employee__in=employees,
            assignment__return_date__isnull=True
        ).distinct()

        return {
            'employee_count': employees.count(),
            'equipment_count': assigned_equipment.count(),
            'total_equipment_value': assigned_equipment.aggregate(
                total=Sum('current_value')
            )['total'] or Decimal('0.00')
        }


# ============================================
# Audit Service
# ============================================

class AuditService:
    """
    Service for audit log operations.

    Examples:
        >>> logs = AuditService.get_user_activity(user, days=7)
    """

    @staticmethod
    def get_user_activity(
        user: User,
        days: int = 30
    ) -> QuerySet:
        """
        Get user activity logs.

        Args:
            user: User instance
            days: Number of days to look back

        Returns:
            QuerySet of audit logs

        Examples:
            >>> activity = AuditService.get_user_activity(request.user, days=7)
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            user=user,
            timestamp__gte=cutoff_date
        ).order_by('-timestamp')

    @staticmethod
    def get_entity_history(
        content_type,
        object_id: int
    ) -> QuerySet:
        """
        Get audit history for a specific entity.

        Args:
            content_type: ContentType of the entity
            object_id: ID of the entity

        Returns:
            QuerySet of audit logs

        Examples:
            >>> from django.contrib.contenttypes.models import ContentType
            >>> ct = ContentType.objects.get_for_model(Equipment)
            >>> history = AuditService.get_entity_history(ct, equipment.id)
        """
        return AuditLog.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-timestamp')


# ============================================
# OTP Service
# ============================================

class OTPService:
    """
    Service for OTP operations.

    Examples:
        >>> otp_record = OTPService.generate_and_send_otp(user)
        >>> is_valid = OTPService.verify_otp(user, "123456")
    """

    @staticmethod
    def generate_and_send_otp(user: User) -> PasswordChangeOTP:
        """
        Generate OTP and send to user email.

        Args:
            user: User requesting OTP

        Returns:
            Created PasswordChangeOTP instance

        Examples:
            >>> otp_record = OTPService.generate_and_send_otp(request.user)
        """
        # Note: Email sending logic should be implemented separately
        # This is just the OTP generation part
        otp_record = PasswordChangeOTP.generate_otp(user)

        # TODO: Implement email sending
        # send_otp_email(user.email, otp_record.otp_code)
        
        try:
            send_mail(
                subject='Parolni tiklash uchun kod',
                message=f'Sizning tasdiqlash kodingiz: {otp_record.otp_code}\n\nBu kod 10 daqiqa davomida amal qiladi.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't stop flow (or handle as needed)
            print(f"Email yuborishda xatolik: {e}")

        return otp_record

    @staticmethod
    def verify_otp(user: User, otp_code: str) -> bool:
        """
        Verify OTP code for user.

        Args:
            user: User instance
            otp_code: OTP code to verify

        Returns:
            True if valid, False otherwise

        Examples:
            >>> is_valid = OTPService.verify_otp(request.user, "123456")
        """
        return PasswordChangeOTP.verify_otp(user, otp_code)


# ============================================
# Export Service
# ============================================

class ExportService:
    """
    Service for data export operations.

    Examples:
        >>> data = ExportService.prepare_equipment_export()
    """

    @staticmethod
    def prepare_equipment_export(
        queryset: Optional[QuerySet] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare equipment data for export.

        Args:
            queryset: Optional equipment queryset (uses all if None)

        Returns:
            List of dictionaries with export data

        Examples:
            >>> data = ExportService.prepare_equipment_export()
        """
        if queryset is None:
            queryset = Equipment.objects.filter(is_active=True)

        queryset = queryset.select_related('category')

        export_data = []
        for equipment in queryset:
            export_data.append({
                'inventory_number': equipment.inventory_number,
                'name': equipment.name,
                'serial_number': equipment.serial_number or '',
                'category': equipment.category.name if equipment.category else '',
                'manufacturer': equipment.manufacturer or '',
                'model': equipment.model or '',
                'status': equipment.get_status_display(),
                'condition': equipment.get_condition_display() if equipment.condition else '',
                'purchase_date': equipment.purchase_date.isoformat() if equipment.purchase_date else '',
                'purchase_price': str(equipment.purchase_price),
                'current_value': str(equipment.current_value),
                'location': equipment.location or '',
            })

        return export_data

    @staticmethod
    def prepare_employee_export(
        queryset: Optional[QuerySet] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare employee data for export.

        Args:
            queryset: Optional employee queryset (uses all if None)

        Returns:
            List of dictionaries with export data

        Examples:
            >>> data = ExportService.prepare_employee_export()
        """
        if queryset is None:
            queryset = Employee.objects.filter(is_active=True)

        queryset = queryset.select_related('department')

        export_data = []
        for employee in queryset:
            export_data.append({
                'employee_id': employee.employee_id,
                'full_name': employee.get_full_name(),
                'email': employee.email or '',
                'phone': employee.phone or '',
                'department': employee.department.name if employee.department else '',
                'position': employee.position or '',
                'hire_date': employee.hire_date.isoformat() if employee.hire_date else '',
                'is_active': 'Yes' if employee.is_active else 'No',
            })

        return export_data
