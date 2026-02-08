"""
Serializers for Inventory Management System.

This module contains all DRF serializers for the inventory system.
Serializers are organized by domain and use base classes/mixins for code reuse.

Architecture:
    - Base serializers provide common functionality
    - Mixins add reusable field patterns
    - Model serializers handle CRUD operations
    - Nested serializers for complex representations
"""

from typing import Dict, Any, Optional
from datetime import datetime

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    Branch, Department, Employee, EquipmentCategory, Equipment,
    Assignment, InventoryCheck, MaintenanceRecord, AuditLog,
    PasswordChangeOTP
)
from .constants import EquipmentStatus, ErrorMessages


# ============================================
# Base Serializers
# ============================================

class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality.

    Provides standard fields and methods used across all serializers.
    Extend this instead of ModelSerializer for consistency.
    """

    def get_user_display(self, user: Optional[User]) -> Optional[str]:
        """
        Get user display name.

        Args:
            user: User instance or None

        Returns:
            Username or None

        Example:
            >>> self.get_user_display(obj.created_by)
            'john_doe'
        """
        return user.username if user else None

    def get_full_name_display(self, user: Optional[User]) -> Optional[str]:
        """
        Get user's full name or username.

        Args:
            user: User instance or None

        Returns:
            Full name or username

        Example:
            >>> self.get_full_name_display(obj.created_by)
            'John Doe'
        """
        if not user:
            return None
        return user.get_full_name() or user.username


class TimestampedSerializer(serializers.Serializer):
    """
    Mixin for serializers that include timestamp fields.

    Adds created_at and updated_at to read-only fields.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# ============================================
# User Serializers
# ============================================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.

    Provides basic user information for nested representations.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj: User) -> str:
        """
        Get user's full name or username as fallback.

        Args:
            obj: User instance

        Returns:
            Full name or username
        """
        return obj.get_full_name() or obj.username


class UserDetailSerializer(UserSerializer):
    """
    Detailed user serializer with additional information.

    Includes staff status and date joined.
    """
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_staff', 'is_superuser', 'date_joined']


# ============================================
# Branch Serializers
# ============================================

class BranchSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for Branch model.

    Includes branch hierarchy, statistics, and full location information.

    Fields:
        - id: Branch ID
        - code: Unique branch code
        - name: Branch name
        - description: Branch description
        - branch_type: Type of branch (HEADQUARTERS, REGIONAL, LOCAL, WAREHOUSE)
        - branch_type_display: Human-readable branch type
        - address: Full address
        - city: City name
        - region: Region/state name
        - country: Country name
        - postal_code: Postal/ZIP code
        - phone: Contact phone number
        - email: Contact email
        - timezone: Branch timezone
        - parent_branch: Parent branch (for hierarchy)
        - parent_branch_name: Parent branch name (read-only)
        - manager: Branch manager employee
        - manager_name: Manager's full name (read-only)
        - area_manager: Area manager employee
        - area_manager_name: Area manager's full name (read-only)
        - employee_count: Count of employees in this branch (read-only)
        - department_count: Count of departments in this branch (read-only)
        - equipment_count: Count of equipment in this branch (read-only)
        - sub_branches_count: Count of direct sub-branches (read-only)
        - is_active: Whether branch is active
        - created_at, updated_at: Timestamps
    """
    branch_type_display = serializers.CharField(
        source='get_branch_type_display',
        read_only=True
    )
    parent_branch_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    area_manager_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    department_count = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    sub_branches_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'code', 'name', 'description', 'branch_type',
            'branch_type_display', 'address', 'city', 'region', 'country',
            'postal_code', 'phone', 'email', 'timezone', 'parent_branch',
            'parent_branch_name', 'manager', 'manager_name', 'area_manager',
            'area_manager_name', 'employee_count', 'department_count',
            'equipment_count', 'sub_branches_count', 'is_active',
            'created_at', 'updated_at', 'created_by', 'last_modified_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'last_modified_by'
        ]

    def get_parent_branch_name(self, obj: Branch) -> Optional[str]:
        """
        Get parent branch name.

        Args:
            obj: Branch instance

        Returns:
            Parent branch name or None

        Example:
            >>> self.get_parent_branch_name(branch)
            'Bosh ofis'
        """
        return obj.parent_branch.name if obj.parent_branch else None

    def get_manager_name(self, obj: Branch) -> Optional[str]:
        """
        Get manager's full name.

        Args:
            obj: Branch instance

        Returns:
            Manager's full name or None

        Example:
            >>> self.get_manager_name(branch)
            'John Doe'
        """
        return obj.manager.get_full_name() if obj.manager else None

    def get_area_manager_name(self, obj: Branch) -> Optional[str]:
        """
        Get area manager's full name.

        Args:
            obj: Branch instance

        Returns:
            Area manager's full name or None

        Example:
            >>> self.get_area_manager_name(branch)
            'Jane Smith'
        """
        return obj.area_manager.get_full_name() if obj.area_manager else None

    def get_employee_count(self, obj: Branch) -> int:
        """
        Get count of employees in this branch.

        Args:
            obj: Branch instance

        Returns:
            Number of active employees

        Example:
            >>> self.get_employee_count(branch)
            25
        """
        return obj.get_employee_count()

    def get_department_count(self, obj: Branch) -> int:
        """
        Get count of departments in this branch.

        Args:
            obj: Branch instance

        Returns:
            Number of active departments

        Example:
            >>> self.get_department_count(branch)
            5
        """
        return obj.departments.filter(is_active=True).count()

    def get_equipment_count(self, obj: Branch) -> int:
        """
        Get count of equipment in this branch.

        Args:
            obj: Branch instance

        Returns:
            Number of active equipment items

        Example:
            >>> self.get_equipment_count(branch)
            150
        """
        return obj.get_equipment_count()

    def get_sub_branches_count(self, obj: Branch) -> int:
        """
        Get count of direct sub-branches.

        Args:
            obj: Branch instance

        Returns:
            Number of active direct sub-branches

        Example:
            >>> self.get_sub_branches_count(branch)
            3
        """
        return obj.sub_branches.filter(is_active=True).count()

    def validate_parent_branch(self, value: Optional[Branch]) -> Optional[Branch]:
        """
        Validate parent branch to prevent circular references.

        Args:
            value: Parent branch instance

        Returns:
            Validated parent branch

        Raises:
            serializers.ValidationError: If circular reference detected

        Example:
            >>> self.validate_parent_branch(parent_branch)
            <Branch: Regional Branch (RB01)>
        """
        if value and self.instance:
            # Check if we're trying to set parent to self
            if value.id == self.instance.id:
                raise serializers.ValidationError(
                    "Filial o'zini ota-filial sifatida belgilay olmaydi"
                )

            # Check if we're trying to set parent to one of our children
            all_sub_branches = self.instance.get_all_sub_branches()
            if value in all_sub_branches:
                raise serializers.ValidationError(
                    "Ota-filial sifatida quyi filiallardan birini belgilab bo'lmaydi"
                )

        return value


class BranchListSerializer(BaseModelSerializer):
    """
    Lightweight serializer for listing branches.

    Provides essential information without expensive calculations.
    Used in list views and select dropdowns for better performance.

    Fields:
        - id: Branch ID
        - code: Branch code
        - name: Branch name
        - branch_type: Type of branch
        - branch_type_display: Human-readable type
        - city: City name
        - parent_branch_name: Parent branch name
        - is_active: Whether branch is active
    """
    branch_type_display = serializers.CharField(
        source='get_branch_type_display',
        read_only=True
    )
    parent_branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = [
            'id', 'code', 'name', 'branch_type', 'branch_type_display',
            'city', 'parent_branch_name', 'is_active'
        ]
        read_only_fields = ['id']

    def get_parent_branch_name(self, obj: Branch) -> Optional[str]:
        """Get parent branch name."""
        return obj.parent_branch.name if obj.parent_branch else None


class BranchDetailSerializer(BranchSerializer):
    """
    Detailed serializer for Branch with full hierarchy information.

    Includes nested sub-branches and comprehensive statistics.
    Used in detail views for complete branch information.

    Additional Fields:
        - sub_branches: List of direct sub-branches
        - full_address: Complete formatted address (read-only)
        - hierarchy_level: Level in branch hierarchy (read-only)
        - is_operational: Whether branch is operational (read-only)
        - created_by_name: Creator's full name (read-only)
        - last_modified_by_name: Last modifier's full name (read-only)
    """
    sub_branches = BranchListSerializer(many=True, read_only=True)
    full_address = serializers.SerializerMethodField()
    hierarchy_level = serializers.SerializerMethodField()
    is_operational = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    last_modified_by_name = serializers.SerializerMethodField()

    class Meta(BranchSerializer.Meta):
        fields = BranchSerializer.Meta.fields + [
            'sub_branches', 'full_address', 'hierarchy_level',
            'is_operational', 'created_by_name', 'last_modified_by_name'
        ]

    def get_full_address(self, obj: Branch) -> str:
        """
        Get complete formatted address.

        Args:
            obj: Branch instance

        Returns:
            Formatted full address

        Example:
            >>> self.get_full_address(branch)
            'Toshkent sh., Chilonzor t., Bunyodkor ko., 12-uy, 100001'
        """
        return obj.get_full_address()

    def get_hierarchy_level(self, obj: Branch) -> int:
        """
        Get branch hierarchy level.

        Args:
            obj: Branch instance

        Returns:
            Hierarchy level (0 for root)

        Example:
            >>> self.get_hierarchy_level(branch)
            2
        """
        return obj.get_hierarchy_level()

    def get_is_operational(self, obj: Branch) -> bool:
        """
        Check if branch is operational.

        Args:
            obj: Branch instance

        Returns:
            True if operational

        Example:
            >>> self.get_is_operational(branch)
            True
        """
        return obj.is_operational()

    def get_created_by_name(self, obj: Branch) -> Optional[str]:
        """Get creator's full name."""
        return self.get_full_name_display(obj.created_by)

    def get_last_modified_by_name(self, obj: Branch) -> Optional[str]:
        """Get last modifier's full name."""
        return self.get_full_name_display(obj.last_modified_by)


# ============================================
# Department Serializers
# ============================================

class DepartmentSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for Department model.

    Includes employee count, manager information, and branch details.

    Fields:
        - id: Department ID
        - code: Unique department code
        - name: Department name
        - description: Department description
        - location: Physical location
        - branch: Branch this department belongs to
        - branch_name: Branch name (read-only)
        - manager: Manager employee (optional)
        - manager_name: Manager's full name (read-only)
        - employee_count: Count of active employees (read-only)
        - is_active: Whether department is active
        - created_at, updated_at: Timestamps
    """
    branch_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'location',
            'branch', 'branch_name', 'manager', 'manager_name',
            'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_branch_name(self, obj: Department) -> Optional[str]:
        """
        Get branch name.

        Args:
            obj: Department instance

        Returns:
            Branch name

        Example:
            >>> self.get_branch_name(department)
            'Toshkent filiali'
        """
        return obj.branch.name if obj.branch else None

    def get_employee_count(self, obj: Department) -> int:
        """
        Get count of active employees in department.

        Args:
            obj: Department instance

        Returns:
            Number of active employees
        """
        return obj.get_employee_count()

    def get_manager_name(self, obj: Department) -> Optional[str]:
        """
        Get manager's full name.

        Args:
            obj: Department instance

        Returns:
            Manager's full name or None
        """
        if obj.manager:
            return obj.manager.get_full_name()
        return None


class DepartmentListSerializer(BaseModelSerializer):
    """
    Lightweight department serializer for list views.

    Optimized for listing with minimal fields including branch.
    """
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'location', 'branch', 'branch_name', 'is_active']
        read_only_fields = ['id']

    def get_branch_name(self, obj: Department) -> Optional[str]:
        """Get branch name."""
        return obj.branch.name if obj.branch else None


# ============================================
# Equipment Category Serializers
# ============================================

class EquipmentCategorySerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for EquipmentCategory model.

    Supports hierarchical categories with parent-child relationships.

    Fields:
        - id: Category ID
        - code: Unique category code
        - name: Category name
        - description: Category description
        - parent: Parent category ID (optional)
        - parent_name: Parent category name (read-only)
        - equipment_count: Count of equipment in category (read-only)
        - is_active: Whether category is active
        - created_at, updated_at: Timestamps
    """
    equipment_count = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentCategory
        fields = [
            'id', 'code', 'name', 'description',
            'parent', 'parent_name', 'equipment_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_equipment_count(self, obj: EquipmentCategory) -> int:
        """
        Get count of equipment in this category.

        Args:
            obj: EquipmentCategory instance

        Returns:
            Number of equipment items
        """
        return obj.get_equipment_count()

    def get_parent_name(self, obj: EquipmentCategory) -> Optional[str]:
        """
        Get parent category name.

        Args:
            obj: EquipmentCategory instance

        Returns:
            Parent category name or None
        """
        return obj.parent.name if obj.parent else None


# ============================================
# Employee Serializers
# ============================================

class EmployeeSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for Employee model.

    Includes branch, department information and equipment assignment count.

    Fields:
        - id: Employee ID
        - employee_id: Unique employee identifier
        - first_name, last_name, middle_name: Name fields
        - full_name: Computed full name (read-only)
        - branch: Branch this employee works at
        - branch_name: Branch name (read-only)
        - department: Department ID
        - department_name: Department name (read-only)
        - position: Job position
        - email, phone: Contact information
        - hire_date, termination_date: Employment dates
        - qr_code: QR code image (read-only)
        - current_equipment_count: Count of assigned equipment (read-only)
        - is_active: Whether employee is active
        - created_at, updated_at: Timestamps
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    current_equipment_count = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'branch', 'branch_name', 'department', 'department_name', 'department_code',
            'position', 'email', 'phone',
            'hire_date', 'termination_date', 'birth_date',
            'address', 'passport_series',
            'emergency_contact', 'emergency_phone',
            'qr_code', 'current_equipment_count',
            'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'qr_code', 'created_at', 'updated_at']

    def get_current_equipment_count(self, obj: Employee) -> int:
        """
        Get count of equipment currently assigned to employee.

        Args:
            obj: Employee instance

        Returns:
            Number of assigned equipment items
        """
        return obj.get_current_equipment_count()


class EmployeeListSerializer(BaseModelSerializer):
    """
    Lightweight employee serializer for list views.

    Optimized for listing with essential fields including branch.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name',
            'branch_name', 'department_name', 'position',
            'email', 'phone', 'is_active', 'qr_code'
        ]
        read_only_fields = ['id']

    def get_qr_code(self, obj):
        """Return full QR code URL."""
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None


class EmployeeDetailSerializer(EmployeeSerializer):
    """
    Detailed employee serializer with assignment history.

    Includes nested assignment information.
    """
    assignment_history = serializers.SerializerMethodField()

    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + ['assignment_history']

    def get_assignment_history(self, obj: Employee):
        """
        Get recent assignment history for employee.

        Args:
            obj: Employee instance

        Returns:
            List of recent assignments
        """
        from .models import Assignment
        recent_assignments = obj.assignments.all().order_by('-assigned_date')[:10]
        return AssignmentListSerializer(recent_assignments, many=True).data


# ============================================
# Equipment Serializers
# ============================================

class EquipmentSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for Equipment model.

    Comprehensive equipment information including financial data,
    warranty status, and current assignment.

    Fields:
        - Basic: id, name, inventory_number, serial_number
        - Branch: branch, branch_name
        - Category: category, category_name
        - Manufacturer: manufacturer, model, specifications
        - Financial: purchase_date, purchase_price, current_value, depreciation_rate
        - Warranty: warranty_expiry, warranty_provider, is_warranty_active
        - Status: status, condition
        - Location: location, default_location
        - Media: qr_code, image
        - Flags: is_critical, requires_training
        - Current state: current_assignment, last_check
        - Audit: is_active, created_at, updated_at
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    current_assignment = serializers.SerializerMethodField()
    last_check = serializers.SerializerMethodField()
    is_warranty_active = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    
    # Make inventory_number optional for auto-generation
    inventory_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Equipment
        fields = [
            # Basic Information
            'id', 'name', 'inventory_number', 'serial_number', 'barcode',

            # Branch
            'branch', 'branch_name',

            # Category
            'category', 'category_name',

            # Manufacturer
            'manufacturer', 'model', 'specifications',

            # Financial
            'purchase_date', 'purchase_price', 'current_value', 'depreciation_rate',

            # Warranty
            'warranty_expiry', 'warranty_provider', 'is_warranty_active',

            # Status
            'status', 'status_display', 'condition', 'condition_display',

            # Location
            'location', 'default_location',

            # Media
            'qr_code', 'image',

            # Flags
            'is_critical', 'requires_training',

            # Current State
            'current_assignment', 'last_check', 'is_available',

            # Audit
            'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'qr_code', 'current_value', 'created_at', 'updated_at']

    def get_current_assignment(self, obj: Equipment) -> Optional[Dict[str, Any]]:
        """
        Get current assignment information.

        Args:
            obj: Equipment instance

        Returns:
            Assignment details or None
        """
        assignment = obj.get_current_assignment()
        if assignment:
            days_assigned = (timezone.now().date() - assignment.assigned_date.date()).days
            return {
                'id': assignment.id,
                'employee': assignment.employee.get_full_name(),
                'employee_id': assignment.employee.employee_id,
                'department': assignment.employee.department.name if assignment.employee.department else None,
                'assigned_date': assignment.assigned_date,
                'days_assigned': days_assigned,
                'is_overdue': assignment.is_overdue()
            }
        return None

    def get_last_check(self, obj: Equipment) -> Optional[Dict[str, Any]]:
        """
        Get last inventory check information.

        Args:
            obj: Equipment instance

        Returns:
            Check details or None
        """
        check = obj.get_last_inventory_check()
        if check:
            return {
                'id': check.id,
                'check_date': check.check_date,
                'checked_by': self.get_user_display(check.checked_by),
                'condition': check.condition,
                'is_functional': check.is_functional,
                'requires_maintenance': check.requires_maintenance
            }
        return None

    def get_is_warranty_active(self, obj: Equipment) -> bool:
        """
        Check if equipment warranty is active.

        Args:
            obj: Equipment instance

        Returns:
            True if warranty is active
        """
        return obj.is_warranty_active()

    def get_is_available(self, obj: Equipment) -> bool:
        """
        Check if equipment is available for assignment.

        Args:
            obj: Equipment instance

        Returns:
            True if available
        """
        return obj.is_available_for_assignment()


class EquipmentListSerializer(BaseModelSerializer):
    """
    Lightweight equipment serializer for list views.

    Optimized for listing with essential fields including branch.
    """
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'inventory_number', 'serial_number',
            'branch_name', 'category_name', 'manufacturer', 'model',
            'status', 'status_display',
            'is_active', 'qr_code'
        ]
        read_only_fields = ['id']

    def get_qr_code(self, obj):
        """Return full QR code URL."""
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None


class EquipmentDetailSerializer(EquipmentSerializer):
    """
    Detailed equipment serializer with full history.

    Includes assignment history, maintenance records, and inventory checks.
    """
    assignment_history = serializers.SerializerMethodField()
    maintenance_history = serializers.SerializerMethodField()
    check_history = serializers.SerializerMethodField()

    class Meta(EquipmentSerializer.Meta):
        fields = EquipmentSerializer.Meta.fields + [
            'assignment_history', 'maintenance_history', 'check_history'
        ]

    def get_assignment_history(self, obj: Equipment):
        """Get recent assignment history."""
        assignments = obj.assignments.all().order_by('-assigned_date')[:20]
        return AssignmentListSerializer(assignments, many=True).data

    def get_maintenance_history(self, obj: Equipment):
        """Get recent maintenance history."""
        records = obj.maintenance_records.all().order_by('-performed_date')[:20]
        return MaintenanceRecordListSerializer(records, many=True).data

    def get_check_history(self, obj: Equipment):
        """Get recent inventory check history."""
        checks = obj.inventory_checks.all().order_by('-check_date')[:20]
        return InventoryCheckListSerializer(checks, many=True).data


# ============================================
# Assignment Serializers
# ============================================

class AssignmentSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for Assignment model.

    Tracks equipment assignment to employees with approval workflow.

    Fields:
        - Core: equipment, employee
        - Dates: assigned_date, expected_return_date, return_date
        - Condition: condition_on_assignment, condition_on_return
        - Workflow: purpose, location, is_temporary
        - Approval: requires_approval, is_approved, approved_by
        - Documentation: notes, return_notes, acknowledgement_signature
        - Audit: assigned_by, returned_by
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_inventory_number = serializers.CharField(source='equipment.inventory_number', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)

    assigned_by_name = serializers.SerializerMethodField()
    returned_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    duration_days = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            # IDs and Names
            'id', 'equipment', 'equipment_name', 'equipment_inventory_number',
            'employee', 'employee_name', 'employee_employee_id', 'department_name',

            # Dates
            'assigned_date', 'expected_return_date', 'return_date',

            # Condition
            'condition_on_assignment', 'condition_on_return',

            # Details
            'purpose', 'location', 'is_temporary',

            # Approval
            'requires_approval', 'is_approved',
            'approved_by', 'approved_by_name',

            # Documentation
            'notes', 'return_notes', 'acknowledgement_signature',

            # Audit
            'assigned_by', 'assigned_by_name',
            'returned_by', 'returned_by_name',

            # Computed
            'duration_days', 'is_overdue', 'is_active',

            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_date', 'created_at', 'updated_at']

    def get_assigned_by_name(self, obj: Assignment) -> Optional[str]:
        """Get name of user who assigned."""
        return self.get_user_display(obj.assigned_by)

    def get_returned_by_name(self, obj: Assignment) -> Optional[str]:
        """Get name of user who processed return."""
        return self.get_user_display(obj.returned_by)

    def get_approved_by_name(self, obj: Assignment) -> Optional[str]:
        """Get name of user who approved."""
        return self.get_user_display(obj.approved_by)

    def get_duration_days(self, obj: Assignment) -> int:
        """Get assignment duration in days."""
        return obj.get_duration_days()

    def get_is_overdue(self, obj: Assignment) -> bool:
        """Check if assignment is overdue."""
        return obj.is_overdue()

    def get_is_active(self, obj: Assignment) -> bool:
        """Check if assignment is currently active."""
        return obj.is_active()


class AssignmentListSerializer(BaseModelSerializer):
    """
    Lightweight assignment serializer for list views.
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'equipment_name', 'employee_name',
            'assigned_date', 'return_date',
            'is_active', 'is_approved'
        ]
        read_only_fields = ['id']

    def get_is_active(self, obj: Assignment) -> bool:
        """Check if assignment is active."""
        return obj.is_active()


# ============================================
# Inventory Check Serializers
# ============================================

class InventoryCheckSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for InventoryCheck model.

    Records equipment verification and condition assessment.
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_inventory_number = serializers.CharField(source='equipment.inventory_number', read_only=True)
    checked_by_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    check_type_display = serializers.CharField(source='get_check_type_display', read_only=True)
    physical_condition_display = serializers.CharField(source='get_physical_condition_display', read_only=True)

    class Meta:
        model = InventoryCheck
        fields = [
            # Equipment
            'id', 'equipment', 'equipment_name', 'equipment_inventory_number',

            # Check Info
            'check_date', 'check_type', 'check_type_display',
            'checked_by', 'checked_by_name',

            # Location
            'location', 'expected_location', 'location_mismatch',

            # Condition
            'condition', 'physical_condition', 'physical_condition_display',
            'is_functional',

            # Issues
            'issues_found', 'requires_maintenance', 'requires_replacement',

            # Confirmation
            'employee_confirmed', 'employee', 'employee_name', 'confirmation_date',

            # Additional
            'photos', 'next_check_date', 'notes',

            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'check_date', 'created_at', 'updated_at']

    def get_checked_by_name(self, obj: InventoryCheck) -> Optional[str]:
        """Get name of user who performed check."""
        return self.get_user_display(obj.checked_by)

    def get_employee_name(self, obj: InventoryCheck) -> Optional[str]:
        """Get name of employee who confirmed."""
        if obj.employee:
            return obj.employee.get_full_name()
        return None


class InventoryCheckListSerializer(BaseModelSerializer):
    """
    Lightweight inventory check serializer for list views.
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    checked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryCheck
        fields = [
            'id', 'equipment_name', 'check_date',
            'checked_by_name', 'is_functional',
            'requires_maintenance', 'employee_confirmed'
        ]
        read_only_fields = ['id']

    def get_checked_by_name(self, obj: InventoryCheck) -> Optional[str]:
        """Get name of user who performed check."""
        return obj.checked_by.username if obj.checked_by else None


# ============================================
# Maintenance Record Serializers
# ============================================

class MaintenanceRecordSerializer(BaseModelSerializer, TimestampedSerializer):
    """
    Serializer for MaintenanceRecord model.

    Tracks equipment maintenance and repair activities.
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_inventory_number = serializers.CharField(source='equipment.inventory_number', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    technician_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRecord
        fields = [
            # Equipment
            'id', 'equipment', 'equipment_name', 'equipment_inventory_number',

            # Type and Status
            'maintenance_type', 'maintenance_type_display',
            'status', 'status_display',
            'priority', 'priority_display',

            # Schedule
            'scheduled_date', 'started_date', 'performed_date', 'next_maintenance_date',

            # Work Description
            'description', 'problem_found', 'solution_applied', 'parts_replaced',

            # Personnel
            'performed_by', 'technician', 'technician_name', 'vendor',

            # Costs
            'estimated_cost', 'actual_cost', 'labor_cost', 'parts_cost', 'total_cost',

            # Additional
            'downtime_hours', 'warranty_claim', 'preventive', 'attachments',
            'notes',

            # Audit
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_technician_name(self, obj: MaintenanceRecord) -> Optional[str]:
        """Get technician's full name."""
        if obj.technician:
            return obj.technician.get_full_name()
        return None

    def get_created_by_name(self, obj: MaintenanceRecord) -> Optional[str]:
        """Get name of user who created record."""
        return self.get_user_display(obj.created_by)

    def get_total_cost(self, obj: MaintenanceRecord) -> float:
        """Calculate total maintenance cost."""
        return obj.get_total_cost()


class MaintenanceRecordListSerializer(BaseModelSerializer):
    """
    Lightweight maintenance record serializer for list views.
    """
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'equipment_name', 'maintenance_type',
            'status', 'status_display',
            'priority', 'priority_display',
            'performed_date', 'actual_cost'
        ]
        read_only_fields = ['id']


# ============================================
# Audit Log Serializers
# ============================================

class AuditLogSerializer(BaseModelSerializer):
    """
    Serializer for AuditLog model.

    Provides comprehensive audit trail information.
    """
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name',
            'action', 'action_display',
            'timestamp',
            'model_name', 'object_repr',
            'description',
            'changes', 'old_values', 'new_values',
            'ip_address', 'user_agent',
            'success', 'error_message'
        ]
        read_only_fields = ['id', 'timestamp']

    def get_user_name(self, obj: AuditLog) -> Optional[str]:
        """Get username of action performer."""
        return self.get_user_display(obj.user)


# ============================================
# Dashboard and Statistics Serializers
# ============================================

class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics.

    Provides aggregated system statistics.
    """
    total_equipment = serializers.IntegerField()
    available_equipment = serializers.IntegerField()
    assigned_equipment = serializers.IntegerField()
    maintenance_equipment = serializers.IntegerField()
    retired_equipment = serializers.IntegerField()

    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()

    total_departments = serializers.IntegerField()

    recent_assignments = AssignmentListSerializer(many=True)
    recent_checks = InventoryCheckListSerializer(many=True)
    pending_maintenance = MaintenanceRecordListSerializer(many=True)


# ============================================
# Import/Export Serializers
# ============================================

class EquipmentCSVImportSerializer(serializers.Serializer):
    """
    Serializer for CSV equipment import.

    Validates equipment data from CSV files.
    """
    inventory_number = serializers.CharField(required=True, max_length=100)
    name = serializers.CharField(required=True, max_length=200)
    serial_number = serializers.CharField(required=False, allow_blank=True, max_length=100)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    manufacturer = serializers.CharField(required=False, allow_blank=True, max_length=100)
    model = serializers.CharField(required=False, allow_blank=True, max_length=100)
    purchase_price = serializers.DecimalField(
        required=False, allow_null=True,
        max_digits=10, decimal_places=2, min_value=0
    )
    purchase_date = serializers.DateField(required=False, allow_null=True)
    warranty_expiry = serializers.DateField(required=False, allow_null=True)
    depreciation_rate = serializers.DecimalField(
        required=False, allow_null=True,
        max_digits=5, decimal_places=2,
        min_value=0, max_value=100
    )
    location = serializers.CharField(required=False, allow_blank=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    assigned_to = serializers.CharField(required=False, allow_blank=True, max_length=50)


class EmployeeCSVImportSerializer(serializers.Serializer):
    """
    Serializer for CSV employee import.

    Validates employee data from CSV files.
    """
    employee_id = serializers.CharField(required=True, max_length=50)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    middle_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    position = serializers.CharField(required=False, allow_blank=True, max_length=100)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    hire_date = serializers.DateField(required=False, allow_null=True)


# ============================================
# OTP and Authentication Serializers
# ============================================

class RequestPasswordChangeOTPSerializer(serializers.Serializer):
    """
    Serializer for requesting password change OTP.

    Validates email for OTP request.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value: str) -> str:
        """
        Validate that email exists in system.

        Args:
            value: Email address

        Returns:
            Validated email

        Raises:
            ValidationError: If email not found
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email bilan foydalanuvchi topilmadi")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for OTP verification.

    Validates email and OTP code.
    """
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_otp_code(self, value: str) -> str:
        """
        Validate OTP code format.

        Args:
            value: OTP code

        Returns:
            Validated OTP code

        Raises:
            ValidationError: If format is invalid
        """
        if not value.isdigit():
            raise serializers.ValidationError("OTP kod faqat raqamlardan iborat bo'lishi kerak")
        return value


class ChangePasswordWithOTPSerializer(serializers.Serializer):
    """
    Serializer for changing password with OTP.

    Validates email, OTP, and new password with confirmation.
    """
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that passwords match.

        Args:
            data: Input data

        Returns:
            Validated data

        Raises:
            ValidationError: If passwords don't match
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Parollar mos kelmadi'
            })
        return data
