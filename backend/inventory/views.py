"""
Views for Inventory Management System.

This module contains API views using Django REST Framework ViewSets.
Following thin controller pattern - business logic is delegated to services.

ViewSets handle:
- HTTP request/response
- Permission checks
- Input validation (via serializers)
- Calling service layer methods
- Formatting responses

Business logic resides in services.py.
"""

import csv
import io
import json
import base64
import logging
from typing import Optional
from datetime import datetime, date

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError

from openai import OpenAI
import google.generativeai as genai
from PIL import Image

from .models import (
    Branch, Department, Employee, EquipmentCategory, Equipment,
    Assignment, InventoryCheck, MaintenanceRecord, AuditLog, PasswordChangeOTP
)
from .serializers import (
    BranchSerializer, BranchListSerializer, BranchDetailSerializer,
    DepartmentSerializer, DepartmentListSerializer,
    EmployeeSerializer, EmployeeListSerializer, EmployeeDetailSerializer,
    EquipmentCategorySerializer,
    EquipmentSerializer, EquipmentListSerializer, EquipmentDetailSerializer,
    AssignmentSerializer, AssignmentListSerializer,
    InventoryCheckSerializer, InventoryCheckListSerializer,
    MaintenanceRecordSerializer, MaintenanceRecordListSerializer,
    DashboardStatsSerializer,
    AuditLogSerializer,
    EquipmentCSVImportSerializer, EmployeeCSVImportSerializer,
    RequestPasswordChangeOTPSerializer, VerifyOTPSerializer, ChangePasswordWithOTPSerializer
)
from .services import (
    BranchService, DepartmentService, EmployeeService,
    EquipmentService, AssignmentService, MaintenanceService,
    InventoryCheckService, AuditService, OTPService, ExportService
)
from .constants import (
    EquipmentStatus, MaintenanceStatus, MaintenancePriority,
    AuditAction, ErrorMessages, SuccessMessages
)

logger = logging.getLogger(__name__)


# ============================================
# Branch ViewSet
# ============================================

class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Branch operations.

    Provides CRUD operations for branches/filials with hierarchy management,
    statistics, and search functionality.

    Endpoints:
        - GET /api/branches/ - List all branches
        - GET /api/branches/{id}/ - Get branch details
        - POST /api/branches/ - Create new branch
        - PUT /api/branches/{id}/ - Update branch
        - DELETE /api/branches/{id}/ - Delete branch
        - GET /api/branches/{id}/statistics/ - Get branch statistics
        - GET /api/branches/{id}/hierarchy/ - Get branch hierarchy tree
        - GET /api/branches/hierarchy_all/ - Get complete hierarchy
        - GET /api/branches/{id}/employees_by_department/ - Get employees grouped by department
        - POST /api/branches/{id}/deactivate/ - Deactivate branch

    Query Parameters:
        - search: Search by code/name/address
        - branch_type: Filter by branch type
        - city: Filter by city
        - is_active: Filter by active status

    Examples:
        GET /api/branches/?search=toshkent&branch_type=REGIONAL
        GET /api/branches/1/statistics/
        GET /api/branches/hierarchy_all/
    """
    queryset = Branch.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return BranchListSerializer
        elif self.action == 'retrieve':
            return BranchDetailSerializer
        return BranchSerializer

    def get_queryset(self):
        """
        Filter branches based on query parameters.

        Supports filtering by:
        - search: code/name/address
        - branch_type: HEADQUARTERS, REGIONAL, LOCAL, WAREHOUSE
        - city: city name
        - is_active: True/False
        """
        queryset = Branch.objects.all()

        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )

        # Branch type filter
        branch_type = self.request.query_params.get('branch_type', None)
        if branch_type:
            queryset = queryset.filter(branch_type=branch_type)

        # City filter
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)

        # Active status filter
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.select_related('parent_branch', 'manager', 'area_manager').order_by('name')

    def perform_create(self, serializer):
        """Create branch using service layer."""
        try:
            branch = BranchService.create_branch(
                data=serializer.validated_data,
                user=self.request.user
            )
            serializer.instance = branch
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    def perform_update(self, serializer):
        """Update branch using service layer."""
        try:
            branch = BranchService.update_branch(
                branch=serializer.instance,
                data=serializer.validated_data,
                user=self.request.user
            )
            serializer.instance = branch
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get comprehensive statistics for a branch.

        Returns employee counts, department counts, equipment statistics,
        and hierarchy information.

        Example:
            GET /api/branches/1/statistics/

            Response:
            {
                "branch_id": 1,
                "branch_name": "Toshkent filiali",
                "total_employees": 25,
                "available_equipment": 45,
                ...
            }
        """
        branch = self.get_object()
        stats = BranchService.get_branch_statistics(branch)
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """
        Get hierarchical tree structure for this branch and its sub-branches.

        Returns nested structure showing all sub-branches recursively.

        Example:
            GET /api/branches/1/hierarchy/

            Response:
            {
                "id": 1,
                "name": "Bosh ofis",
                "children": [
                    {
                        "id": 2,
                        "name": "Toshkent filiali",
                        "children": [...]
                    }
                ]
            }
        """
        branch = self.get_object()
        hierarchy = BranchService.get_branch_hierarchy(branch)
        return Response(hierarchy, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def hierarchy_all(self, request):
        """
        Get complete hierarchy of all branches starting from root branches.

        Returns list of hierarchical trees for all root branches (branches
        without parent branches).

        Example:
            GET /api/branches/hierarchy_all/

            Response:
            [
                {
                    "id": 1,
                    "name": "Bosh ofis",
                    "children": [...]
                },
                {
                    "id": 5,
                    "name": "Boshqa bosh ofis",
                    "children": [...]
                }
            ]
        """
        hierarchies = BranchService.get_all_branches_hierarchy()
        return Response(hierarchies, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def employees_by_department(self, request, pk=None):
        """
        Get all employees in this branch grouped by their departments.

        Example:
            GET /api/branches/1/employees_by_department/

            Response:
            {
                "IT bo'limi": [
                    {"id": 1, "name": "John Doe", ...},
                    {"id": 2, "name": "Jane Smith", ...}
                ],
                "HR bo'limi": [...]
            }
        """
        branch = self.get_object()
        employees_by_dept = BranchService.get_branch_employees_by_department(branch)

        # Serialize the employees
        result = {}
        for dept_name, employees in employees_by_dept.items():
            from .serializers import EmployeeListSerializer
            result[dept_name] = EmployeeListSerializer(employees, many=True).data

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a branch and optionally its sub-branches.

        Request Body:
            {
                "cascade": true  // Optional, default false
            }

        Example:
            POST /api/branches/1/deactivate/
            {
                "cascade": true
            }

            Response:
            {
                "message": "Filial nofaollashtirildi"
            }
        """
        branch = self.get_object()
        cascade = request.data.get('cascade', False)

        try:
            BranchService.deactivate_branch(
                branch=branch,
                user=request.user,
                cascade=cascade
            )
            return Response(
                {'message': 'Filial muvaffaqiyatli nofaollashtirildi'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error deactivating branch {branch.id}: {str(e)}")
            return Response(
                {'error': 'Filialni nofaollashtirish amalga oshmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# Department ViewSet
# ============================================

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department operations.

    Provides CRUD operations for departments with search functionality.

    Endpoints:
        - GET /api/departments/ - List all departments
        - GET /api/departments/{id}/ - Get department details
        - POST /api/departments/ - Create new department
        - PUT /api/departments/{id}/ - Update department
        - DELETE /api/departments/{id}/ - Delete department

    Query Parameters:
        - search: Search by department name

    Examples:
        GET /api/departments/?search=IT
    """
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Use list serializer for list action, detail for others."""
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer

    def get_queryset(self):
        """
        Get departments with optional search filtering.

        Returns:
            Filtered QuerySet of departments
        """
        queryset = Department.objects.filter(is_active=True).order_by('name')

        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))

        return queryset

    def perform_create(self, serializer):
        """Set created_by when creating department."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set last_modified_by when updating department."""
        serializer.save(last_modified_by=self.request.user)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get department statistics.

        Returns employee count, equipment count, and total value.

        Examples:
            GET /api/departments/1/statistics/
        """
        department = self.get_object()
        stats = DepartmentService.get_department_statistics(department)
        return Response(stats)


# ============================================
# Employee ViewSet
# ============================================

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee operations.

    Provides CRUD operations for employees with search and filtering.

    Endpoints:
        - GET /api/employees/ - List all employees
        - GET /api/employees/{id}/ - Get employee details
        - POST /api/employees/ - Create new employee
        - PUT /api/employees/{id}/ - Update employee
        - DELETE /api/employees/{id}/ - Delete employee
        - GET /api/employees/export_csv/ - Export to CSV
        - POST /api/employees/import_csv/ - Import from CSV

    Query Parameters:
        - search: Search by name, employee_id, or email
        - department: Filter by department ID
        - is_active: Filter by active status (true/false)

    Examples:
        GET /api/employees/?search=john&department=1&is_active=true
    """
    queryset = Employee.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'retrieve':
            return EmployeeDetailSerializer
        return EmployeeSerializer

    def get_queryset(self):
        """
        Get employees with optional filtering.

        Returns:
            Filtered QuerySet of employees
        """
        queryset = Employee.objects.select_related('department', 'branch')

        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(middle_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )

        # Department filter
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department_id=department)

        # Active status filter
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')

        return queryset.order_by('last_name', 'first_name')

    def perform_create(self, serializer):
        """Create employee with QR code generation."""
        employee = EmployeeService.create_employee(
            data=serializer.validated_data,
            user=self.request.user,
            generate_qr=True
        )
        serializer.instance = employee

    def perform_update(self, serializer):
        """Set last_modified_by when updating employee."""
        serializer.save(last_modified_by=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_csv(self, request):
        """
        Export employees to CSV file.

        Returns:
            CSV file download response

        Examples:
            GET /api/employees/export_csv/
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="hodimlar.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Hodim ID', 'Ism', 'Familiya', 'Otasining ismi',
            'Bo\'lim', 'Lavozim', 'Email', 'Telefon', 'Tug\'ilgan sana',
            'Ishga qabul qilingan sana', 'Manzil', 'Faol'
        ])

        employees = self.get_queryset()
        for employee in employees:
            writer.writerow([
                employee.id,
                employee.employee_id,
                employee.first_name,
                employee.last_name,
                employee.middle_name or '',
                employee.department.name if employee.department else '',
                employee.position or '',
                employee.email or '',
                employee.phone or '',
                employee.birth_date or '',
                employee.hire_date,
                employee.address or '',
                'Ha' if employee.is_active else 'Yo\'q'
            ])

        return response

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], authentication_classes=[TokenAuthentication])
    def import_csv(self, request):
        """
        Import employees from CSV file.

        Accepts CSV file with employee data. Creates new employees or updates existing.

        Returns:
            JSON with created count, updated count, and errors

        Examples:
            POST /api/employees/import_csv/ with file in multipart/form-data
        """
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response(
                {'error': 'CSV fayl topilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Faqat CSV fayllar qabul qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_count = 0
            updated_count = 0
            errors = []

            # Get or create a default branch for imports
            default_branch = Branch.objects.filter(is_active=True).first()
            if not default_branch:
                return Response(
                    {'error': 'Tizimda filial mavjud emas. Avval filial yarating.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Get branch from CSV or use default
                    branch_name = (row.get('branch') or row.get('Filial') or '').strip()
                    branch = default_branch
                    if branch_name:
                        branch = Branch.objects.filter(name__icontains=branch_name, is_active=True).first() or default_branch

                    # Get or create department
                    department_name = (row.get('department') or row.get('Bo\'lim') or '').strip()
                    department = None
                    if department_name:
                        department, _ = Department.objects.get_or_create(
                            name=department_name,
                            branch=branch,
                            defaults={
                                'code': department_name.upper().replace(' ', '_')[:20],
                                'description': f'{department_name}',
                                'created_by': request.user
                            }
                        )

                    # Parse employee data
                    employee_id = (row.get('employee_id') or row.get('Hodim ID') or '').strip()
                    if not employee_id:
                        errors.append(f"Qator {row_num}: Hodim ID yo'q")
                        continue

                    # Parse dates
                    birth_date = row.get('birth_date') or row.get('Tug\'ilgan sana') or ''
                    hire_date = row.get('hire_date') or row.get('Ishga qabul qilingan sana') or ''

                    if birth_date and birth_date.strip():
                        try:
                            birth_date = datetime.strptime(birth_date.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            birth_date = None
                    else:
                        birth_date = None

                    if hire_date and hire_date.strip():
                        try:
                            hire_date = datetime.strptime(hire_date.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            hire_date = date.today()
                    else:
                        hire_date = date.today()

                    # Parse email
                    email_val = (row.get('email') or row.get('Email') or '').strip()
                    email_val = email_val if email_val else None

                    # Create or update employee
                    employee, created = Employee.objects.update_or_create(
                        employee_id=employee_id,
                        defaults={
                            'first_name': (row.get('first_name') or row.get('Ism') or '').strip(),
                            'last_name': (row.get('last_name') or row.get('Familiya') or '').strip(),
                            'middle_name': (row.get('middle_name') or row.get('Otasining ismi') or '').strip(),
                            'branch': branch,
                            'department': department,
                            'position': (row.get('position') or row.get('Lavozim') or '').strip(),
                            'email': email_val,
                            'phone': (row.get('phone') or row.get('Telefon') or '').strip(),
                            'birth_date': birth_date,
                            'hire_date': hire_date,
                            'address': (row.get('address') or row.get('Manzil') or '').strip(),
                            'is_active': (row.get('is_active') or row.get('Faol') or '').strip().lower() in ['ha', 'yes', '1', 'true', 'active', ''],
                            'last_modified_by': request.user
                        }
                    )

                    if created:
                        employee.created_by = request.user
                        employee.save()
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Qator {row_num}: {str(e)}")

            return Response({
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            })

        except Exception as e:
            logger.error(f'Employee CSV import failed: {str(e)}', exc_info=True)
            return Response(
                {'error': f'CSV faylni o\'qishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# Equipment Category ViewSet
# ============================================

class EquipmentCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Equipment Category operations.

    Provides CRUD operations for equipment categories.

    Endpoints:
        - GET /api/categories/ - List all categories
        - GET /api/categories/{id}/ - Get category details
        - POST /api/categories/ - Create new category
        - PUT /api/categories/{id}/ - Update category
        - DELETE /api/categories/{id}/ - Delete category

    Query Parameters:
        - search: Search by name or code

    Examples:
        GET /api/categories/?search=computer
    """
    queryset = EquipmentCategory.objects.all()
    serializer_class = EquipmentCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Get categories with optional search filtering."""
        queryset = EquipmentCategory.objects.filter(is_active=True).order_by('name')

        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        """Save new category."""
        serializer.save()

    def perform_update(self, serializer):
        """Update category."""
        serializer.save()


# ============================================
# Equipment ViewSet
# ============================================

class EquipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Equipment operations.

    Provides comprehensive equipment management including assignment,
    return, inventory checks, and CSV import/export.

    Endpoints:
        - GET /api/equipment/ - List all equipment
        - GET /api/equipment/{id}/ - Get equipment details
        - POST /api/equipment/ - Create new equipment
        - PUT /api/equipment/{id}/ - Update equipment
        - DELETE /api/equipment/{id}/ - Delete equipment
        - POST /api/equipment/{id}/assign/ - Assign to employee
        - POST /api/equipment/{id}/return_equipment/ - Return equipment
        - POST /api/equipment/{id}/inventory_check/ - Record inventory check
        - GET /api/equipment/{id}/scan/ - Get equipment via QR scan
        - GET /api/equipment/export_csv/ - Export to CSV
        - POST /api/equipment/import_csv/ - Import from CSV
        - POST /api/equipment/scan_invoice_gemini/ - Scan invoice with AI

    Query Parameters:
        - search: Search by name, inventory number, or serial number
        - category: Filter by category ID
        - status: Filter by status

    Examples:
        GET /api/equipment/?search=laptop&category=1&status=AVAILABLE
    """
    queryset = Equipment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return EquipmentListSerializer
        elif self.action == 'retrieve':
            return EquipmentDetailSerializer
        return EquipmentSerializer

    def get_queryset(self):
        """Get equipment with optional filtering."""
        queryset = Equipment.objects.select_related('category', 'branch').filter(is_active=True)

        # DEBUG LOGGING
        logger.error(f"DEBUG_EQUIPMENT_LIST: Initial Active Count: {queryset.count()}")

        # Search filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(inventory_number__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(manufacturer__icontains=search) |
                Q(model__icontains=search)
            )
            logger.error(f"DEBUG_EQUIPMENT_LIST: After Search '{search}': {queryset.count()}")

        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
            logger.error(f"DEBUG_EQUIPMENT_LIST: After Category '{category}': {queryset.count()}")

        # Status filter
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            logger.error(f"DEBUG_EQUIPMENT_LIST: After Status '{status_filter}': {queryset.count()}")
            
        final_count = queryset.count()
        logger.error(f"DEBUG_EQUIPMENT_LIST: Final Count: {final_count}")
        if final_count > 0:
             logger.error(f"DEBUG_EQUIPMENT_LIST: First item: {queryset.order_by('-created_at').first().inventory_number}")

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Create equipment with service layer."""
        equipment = EquipmentService.create_equipment(
            data=serializer.validated_data,
            user=self.request.user,
            generate_qr=True
        )
        serializer.instance = equipment

    def perform_update(self, serializer):
        """Update equipment with service layer."""
        equipment = EquipmentService.update_equipment(
            equipment=self.get_object(),
            data=serializer.validated_data,
            user=self.request.user
        )
        serializer.instance = equipment

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign equipment to an employee.

        Request Body:
            - employee_id: ID of employee (required)
            - notes: Assignment notes (optional)
            - expected_return_date: Expected return date (optional)

        Returns:
            Assignment details

        Examples:
            POST /api/equipment/1/assign/
            {
                "employee_id": 5,
                "notes": "For project work"
            }
        """
        equipment = self.get_object()
        employee_id = request.data.get('employee_id')
        notes = request.data.get('notes', '')
        expected_return_date = request.data.get('expected_return_date', None)

        if not employee_id:
            return Response(
                {'error': 'Hodim ID kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee = Employee.objects.get(id=employee_id, is_active=True)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Hodim topilmadi yoki faol emas'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Parse expected return date
        if expected_return_date:
            try:
                expected_return_date = datetime.strptime(expected_return_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Noto\'g\'ri sana formati (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            assignment = AssignmentService.assign_equipment(
                equipment=equipment,
                employee=employee,
                user=request.user,
                notes=notes,
                expected_return_date=expected_return_date
            )

            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def return_equipment(self, request, pk=None):
        """
        Return equipment from employee.

        Request Body:
            - condition: Equipment condition on return (optional)
            - notes: Return notes (optional)

        Returns:
            Updated assignment details

        Examples:
            POST /api/equipment/1/return_equipment/
            {
                "condition": "GOOD",
                "notes": "All working fine"
            }
        """
        equipment = self.get_object()
        condition = request.data.get('condition', '')
        notes = request.data.get('notes', '')

        # Get current assignment
        current_assignment = AssignmentService.get_active_assignments(
            equipment=equipment
        ).first()

        if not current_assignment:
            return Response(
                {'error': ErrorMessages.EQUIPMENT_NOT_ASSIGNED},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            assignment = AssignmentService.return_equipment(
                assignment=current_assignment,
                user=request.user,
                condition=condition,
                notes=notes
            )

            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data)

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def inventory_check(self, request, pk=None):
        """
        Record inventory check for equipment.

        Request Body:
            - check_type: Type of check (required)
            - notes: Check notes (optional)

        Returns:
            Created inventory check details

        Examples:
            POST /api/equipment/1/inventory_check/
            {
                "check_type": "SCHEDULED",
                "notes": "Regular monthly check"
            }
        """
        equipment = self.get_object()
        check_type = request.data.get('check_type', 'SCHEDULED')
        notes = request.data.get('notes', '')
        location = request.data.get('location', '')
        condition = request.data.get('condition', '')
        is_functional = request.data.get('is_functional', True)

        try:
            check = InventoryCheckService.create_check(
                equipment=equipment,
                check_type=check_type,
                user=request.user,
                notes=notes,
                location=location,
                condition=condition,
                is_functional=is_functional,
            )

            serializer = InventoryCheckSerializer(check)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def scan(self, request, pk=None):
        """
        Get equipment details via QR code scan.

        Returns:
            Full equipment details

        Examples:
            GET /api/equipment/1/scan/
        """
        equipment = self.get_object()
        serializer = EquipmentDetailSerializer(equipment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_csv(self, request):
        """
        Export equipment to CSV file.

        Returns:
            CSV file download response

        Examples:
            GET /api/equipment/export_csv/
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="qurilmalar.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nomi', 'Kategoriya', 'Seriya raqami', 'Inventar raqami',
            'Ishlab chiqaruvchi', 'Model', 'Sotib olingan sana', 'Narxi',
            'Holati', 'Joylashuvi', 'Kafolat muddati', 'Tavsif'
        ])

        equipments = self.get_queryset()
        for equipment in equipments:
            writer.writerow([
                equipment.id,
                equipment.name,
                equipment.category.name if equipment.category else '',
                equipment.serial_number or '',
                equipment.inventory_number,
                equipment.manufacturer or '',
                equipment.model or '',
                equipment.purchase_date or '',
                equipment.purchase_price,
                equipment.get_status_display(),
                equipment.location or '',
                equipment.warranty_expiry or '',
                equipment.notes or ''
            ])

        return response

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], authentication_classes=[TokenAuthentication])
    def import_csv(self, request):
        """
        Import equipment from CSV file.

        Accepts CSV file with equipment data. Creates new equipment or updates existing.

        Returns:
            JSON with created count, updated count, and errors

        Examples:
            POST /api/equipment/import_csv/ with file in multipart/form-data
        """
        csv_file = request.FILES.get('file')

        if not csv_file:
            return Response(
                {'error': 'CSV fayl topilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Faqat CSV fayllar qabul qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            created_count = 0
            updated_count = 0
            errors = []

            # Get or create a default branch for imports
            default_branch = Branch.objects.filter(is_active=True).first()
            if not default_branch:
                return Response(
                    {'error': 'Tizimda filial mavjud emas. Avval filial yarating.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"CSV import started for equipment. File: {csv_file.name}")

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Get branch from CSV or use default
                    branch_name = (row.get('branch') or row.get('Filial') or '').strip()
                    branch = default_branch
                    if branch_name:
                        branch = Branch.objects.filter(name__icontains=branch_name, is_active=True).first() or default_branch

                    # Get or create category
                    category_name = (row.get('category') or row.get('Kategoriya') or '').strip()
                    category = None
                    if category_name:
                        category, _ = EquipmentCategory.objects.get_or_create(
                            name=category_name,
                            defaults={
                                'code': category_name.upper().replace(' ', '_')[:20],
                                'description': f'{category_name} kategoriyasi',
                            }
                        )

                    # Parse status
                    status_map = {
                        'Mavjud': 'AVAILABLE',
                        'Tayinlangan': 'ASSIGNED',
                        'Ta\'mirlashda': 'MAINTENANCE',
                        'Yaroqsiz': 'RETIRED',
                        'AVAILABLE': 'AVAILABLE',
                        'ASSIGNED': 'ASSIGNED',
                        'MAINTENANCE': 'MAINTENANCE',
                        'RETIRED': 'RETIRED',
                        'WORKING': 'AVAILABLE'
                    }
                    status_str = (row.get('status') or row.get('Holati') or 'WORKING').strip()
                    status_value = status_map.get(status_str, 'AVAILABLE')

                    # Parse inventory number
                    inventory_number = (row.get('inventory_number') or row.get('Inventar raqami') or '').strip()
                    if not inventory_number:
                        errors.append(f"Qator {row_num}: Inventar raqami yo'q")
                        continue

                    # Parse numeric fields
                    depreciation_rate = row.get('depreciation_rate') or row.get('Amortizatsiya stavkasi') or '0'
                    try:
                        depreciation_rate = float(depreciation_rate)
                    except (ValueError, TypeError):
                        depreciation_rate = 0.0

                    purchase_price = row.get('purchase_price') or row.get('Narxi') or '0'
                    try:
                        purchase_price = float(purchase_price)
                    except (ValueError, TypeError):
                        purchase_price = 0.0

                    # Parse dates
                    purchase_date = row.get('purchase_date') or row.get('Sotib olingan sana') or ''
                    warranty_expiry = row.get('warranty_expiry') or row.get('Kafolat muddati') or ''

                    if purchase_date and purchase_date.strip():
                        try:
                            purchase_date = datetime.strptime(purchase_date.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            purchase_date = None
                    else:
                        purchase_date = None

                    if warranty_expiry and warranty_expiry.strip():
                        try:
                            warranty_expiry = datetime.strptime(warranty_expiry.strip(), '%Y-%m-%d').date()
                        except ValueError:
                            warranty_expiry = None
                    else:
                        warranty_expiry = None

                    # Generate serial number if empty
                    serial_number = (row.get('serial_number') or row.get('Seriya raqami') or '').strip()
                    if not serial_number:
                        serial_number = f"SN-{inventory_number}"

                    # Create or update equipment
                    equipment, created = Equipment.objects.update_or_create(
                        inventory_number=inventory_number,
                        defaults={
                            'name': (row.get('name') or row.get('Nomi') or '').strip(),
                            'branch': branch,
                            'category': category,
                            'serial_number': serial_number,
                            'manufacturer': (row.get('manufacturer') or row.get('Ishlab chiqaruvchi') or '').strip(),
                            'model': (row.get('model') or row.get('Model') or '').strip(),
                            'purchase_date': purchase_date,
                            'purchase_price': purchase_price,
                            'depreciation_rate': depreciation_rate,
                            'status': status_value,
                            'location': (row.get('location') or row.get('Joylashuvi') or '').strip(),
                            'warranty_expiry': warranty_expiry,
                            'notes': (row.get('description') or row.get('Tavsif') or '').strip(),
                            'last_modified_by': request.user
                        }
                    )

                    if created:
                        equipment.created_by = request.user
                        equipment.calculate_current_value()
                        equipment.save()
                        created_count += 1
                    else:
                        equipment.calculate_current_value()
                        equipment.save()
                        updated_count += 1

                except Exception as e:
                    error_msg = f"Qator {row_num}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"Equipment import row error: {error_msg}", exc_info=True)

            logger.info(f"Equipment CSV import completed. Created: {created_count}, Updated: {updated_count}, Errors: {len(errors)}")

            return Response({
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            })

        except Exception as e:
            logger.error(f'Equipment CSV import failed: {str(e)}', exc_info=True)
            return Response(
                {'error': f'CSV faylni o\'qishda xatolik: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def scan_invoice_gemini(self, request):
        """
        Scan invoice image using Google Gemini Vision AI.

        Extracts equipment information from invoice images automatically.

        Request Body:
            - file: Image file (JPG, PNG, WEBP) - max 4MB

        Returns:
            JSON with extracted invoice data

        Examples:
            POST /api/equipment/scan_invoice_gemini/ with file in multipart/form-data
        """
        logger.info("=== GEMINI INVOICE SCAN STARTED ===")
        image_file = request.FILES.get('file')

        if not image_file:
            logger.error("No file uploaded")
            return Response(
                {'error': 'Rasm fayli topilmadi'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"File received: {image_file.name}, size: {image_file.size}, type: {image_file.content_type}")

        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Faqat rasm fayllar qabul qilinadi (JPG, PNG, WEBP)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size (max 4MB for Gemini)
        max_size = 4 * 1024 * 1024
        if image_file.size > max_size:
            return Response(
                {'error': 'Rasm hajmi 4MB dan oshmasligi kerak'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get Gemini API key
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key or api_key == 'your-gemini-api-key-here':
                return Response(
                    {'error': 'Google Gemini API key sozlanmagan. .env faylida GEMINI_API_KEY ni sozlang.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Configure Gemini
            genai.configure(api_key=api_key)

            # Load and prepare image
            img = Image.open(image_file)

            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

            # Initialize Gemini model
            model = genai.GenerativeModel('gemini-2.0-flash-exp')

            # Prepare prompt
            prompt = """
Bu nakladnoy (Ð½Ð°ÐºÐ»Ð°Ð´Ð½Ð°Ñ) rasmidan qurilmalar ma'lumotlarini chiqarib bering.

Quyidagi JSON formatda qaytaring (faqat JSON, boshqa matn yo'q):
{
  "invoice_date": "2025-01-09",
  "supplier": "Yetkazib beruvchi nomi",
  "items": [
    {
      "name": "Qurilma to'liq nomi",
      "quantity": 1,
      "price": 0,
      "serial_number": "seriya raqami agar bor bo'lsa",
      "manufacturer": "Ishlab chiqaruvchi",
      "model": "Model",
      "category": "kategoriya (masalan: Kompyuter, Monitor, Printer)",
      "warranty_months": 12
    }
  ]
}

MUHIM qoidalar:
1. invoice_date - faqat STRING formatda "YYYY-MM-DD" (masalan: "2025-01-09")
2. Har bir mahsulot alohida obyekt bo'lishi kerak
3. Agar seriya raqami yo'q bo'lsa, null yoki empty string qo'ying
4. price - faqat raqam (number), string emas
5. quantity - faqat raqam (number), string emas
6. Agar miqdor (ÐºÐ¾Ð»-Ð²Ð¾/qty) ko'rsatilmagan bo'lsa, 1 qo'ying
7. Kategoriyani mahsulot nomidan aniqlang
8. Kafolat muddati (Ð³Ð°Ñ€Ð°Ð½Ñ‚Ð¸Ñ) - faqat raqam (number) oylar sonida
9. O'zbek, rus, ingliz tillarini tushunasiz
10. FAQAT to'g'ri JSON qaytaring, boshqa hech narsa yo'q!
"""

            # Generate content with image
            response = model.generate_content([prompt, img])

            # Get response text
            result_text = response.text.strip()

            # Extract JSON from response
            try:
                # Remove markdown code blocks if present
                if result_text.startswith('```'):
                    start_idx = result_text.find('{')
                    end_idx = result_text.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = result_text[start_idx:end_idx]
                    else:
                        json_str = result_text
                else:
                    json_str = result_text

                result_data = json.loads(json_str)

                # Validate response structure
                if 'items' not in result_data or not isinstance(result_data['items'], list):
                    return Response(
                        {'error': 'AI javobida "items" ro\'yxati topilmadi', 'raw_response': result_text},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return Response({
                    'success': True,
                    'data': result_data,
                    'ai_model': 'Google Gemini 2.0 Flash (BEPUL)'
                })

            except json.JSONDecodeError as e:
                logger.error(f'Gemini JSON parse error: {str(e)}', exc_info=True)
                return Response(
                    {'error': 'AI dan noto\'g\'ri javob keldi', 'raw_response': result_text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f'Gemini invoice scanning failed: {str(e)}', exc_info=True)
            return Response(
                {'error': f'Nakladnoyni skanerlashda xatolik: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# Assignment ViewSet
# ============================================

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assignment operations.

    Provides CRUD operations for equipment assignments with filtering
    and historical data queries.

    Endpoints:
        - GET /api/assignments/ - List all assignments
        - GET /api/assignments/{id}/ - Get assignment details
        - POST /api/assignments/ - Create new assignment
        - PUT /api/assignments/{id}/ - Update assignment
        - DELETE /api/assignments/{id}/ - Delete assignment
        - GET /api/assignments/history/ - Get historical assignment data
        - GET /api/assignments/dashboard_stats/ - Get dashboard statistics
        - GET /api/assignments/export_csv/ - Export to CSV

    Query Parameters:
        - equipment: Filter by equipment ID
        - employee: Filter by employee ID
        - active_only: Filter active assignments (true/false)
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - date: Filter specific date (YYYY-MM-DD)

    Examples:
        GET /api/assignments/?employee=1&active_only=true
        GET /api/assignments/history/?date=2025-01-15
    """
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return AssignmentListSerializer
        return AssignmentSerializer

    def get_queryset(self):
        """Get assignments with optional filtering."""
        queryset = Assignment.objects.select_related('equipment', 'employee', 'assigned_by')

        # Equipment filter
        equipment = self.request.query_params.get('equipment', None)
        if equipment:
            queryset = queryset.filter(equipment_id=equipment)

        # Employee filter
        employee = self.request.query_params.get('employee', None)
        if employee:
            queryset = queryset.filter(employee_id=employee)

        # Active only filter
        active_only = self.request.query_params.get('active_only', None)
        if active_only == 'true':
            queryset = queryset.filter(returned_date__isnull=True)

        # Date filters
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        specific_date = self.request.query_params.get('date', None)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(assigned_date__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(assigned_date__lte=date_to_obj)
            except ValueError:
                pass

        if specific_date:
            try:
                specific_date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
                queryset = queryset.filter(assigned_date=specific_date_obj)
            except ValueError:
                pass

        return queryset.order_by('-assigned_date')

    def perform_create(self, serializer):
        """Set assigned_by when creating assignment."""
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get historical assignment data for specific date.

        Shows which equipment was assigned to whom on a specific date.

        Query Parameters:
            - date: Specific date (YYYY-MM-DD) - required

        Returns:
            JSON with active assignments, checks, and maintenance on that date

        Examples:
            GET /api/assignments/history/?date=2025-01-15
        """
        specific_date = request.query_params.get('date', None)

        if not specific_date:
            return Response(
                {'error': 'Sana kiritilishi shart (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Noto\'g\'ri sana formati. To\'g\'ri format: YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get active assignments on that date
        active_assignments = Assignment.objects.filter(
            assigned_date__lte=date_obj
        ).filter(
            Q(returned_date__isnull=True) | Q(returned_date__gte=date_obj)
        ).select_related('equipment', 'employee', 'assigned_by')

        # Get inventory checks up to that date
        inventory_checks = InventoryCheck.objects.filter(
            check_date__lte=date_obj
        ).select_related('equipment', 'checked_by').order_by('-check_date')

        # Get maintenance records up to that date
        maintenance_records = MaintenanceRecord.objects.filter(
            created_at__lte=date_obj
        ).select_related('equipment').order_by('-created_at')

        return Response({
            'date': specific_date,
            'active_assignments': AssignmentSerializer(active_assignments, many=True).data,
            'inventory_checks_count': inventory_checks.count(),
            'maintenance_records_count': maintenance_records.count(),
            'total_assigned_equipment': active_assignments.count(),
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def dashboard_stats(self, request):
        """
        Get dashboard statistics.

        Returns:
            JSON with equipment counts, recent assignments, and checks

        Examples:
            GET /api/assignments/dashboard_stats/
        """
        total_equipment = Equipment.objects.count()
        available_equipment = Equipment.objects.filter(status=EquipmentStatus.AVAILABLE).count()
        assigned_equipment = Equipment.objects.filter(status=EquipmentStatus.ASSIGNED).count()
        maintenance_equipment = Equipment.objects.filter(status=EquipmentStatus.MAINTENANCE).count()
        retired_equipment = Equipment.objects.filter(status=EquipmentStatus.RETIRED).count()
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        total_departments = Department.objects.count()

        # Get recent assignments (last 10)
        try:
            recent_assignments = Assignment.objects.select_related(
                'equipment', 'employee'
            ).order_by('-assigned_date')[:10]
        except Exception as e:
            logger.warning(f"Error fetching recent assignments: {e}")
            recent_assignments = Assignment.objects.none()

        # Get recent inventory checks (last 10)
        try:
            recent_checks = InventoryCheck.objects.select_related(
                'equipment', 'checked_by'
            ).order_by('-check_date')[:10]
        except Exception as e:
            logger.warning(f"Error fetching recent checks: {e}")
            recent_checks = InventoryCheck.objects.none()

        # Get pending maintenance (scheduled or in progress)
        try:
            pending_maintenance = MaintenanceRecord.objects.filter(
                status__in=[MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
            ).select_related('equipment').order_by('-scheduled_date')[:10]
        except Exception as e:
            logger.warning(f"Error fetching pending maintenance: {e}")
            pending_maintenance = MaintenanceRecord.objects.none()

        stats = {
            'total_equipment': total_equipment,
            'available_equipment': available_equipment,
            'assigned_equipment': assigned_equipment,
            'maintenance_equipment': maintenance_equipment,
            'retired_equipment': retired_equipment,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_departments': total_departments,
            'recent_assignments': recent_assignments,
            'recent_checks': recent_checks,
            'pending_maintenance': pending_maintenance
        }

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export assignments to CSV file.

        Returns:
            CSV file download response

        Examples:
            GET /api/assignments/export_csv/
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="tayinlashlar.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Qurilma', 'Inventar raqami', 'Hodim', 'Hodim ID',
            'Bo\'lim', 'Tayinlangan sana', 'Qaytarilgan sana',
            'Holati (tayinlash)', 'Holati (qaytarish)', 'Izoh'
        ])

        queryset = self.get_queryset()
        for assignment in queryset:
            writer.writerow([
                assignment.id,
                assignment.equipment.name,
                assignment.equipment.inventory_number,
                assignment.employee.get_full_name(),
                assignment.employee.employee_id,
                assignment.employee.department.name if assignment.employee.department else '',
                assignment.assigned_date,
                assignment.returned_date or '',
                assignment.condition_on_assignment or '',
                assignment.condition_on_return or '',
                assignment.notes or ''
            ])

        return response


# ============================================
# Inventory Check ViewSet
# ============================================

class InventoryCheckViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Inventory Check operations.

    Provides CRUD operations for inventory checks with filtering.

    Endpoints:
        - GET /api/inventory-checks/ - List all checks
        - GET /api/inventory-checks/{id}/ - Get check details
        - POST /api/inventory-checks/ - Create new check
        - PUT /api/inventory-checks/{id}/ - Update check
        - DELETE /api/inventory-checks/{id}/ - Delete check
        - GET /api/inventory-checks/export_csv/ - Export to CSV

    Query Parameters:
        - equipment: Filter by equipment ID
        - check_type: Filter by check type
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - date: Filter specific date (YYYY-MM-DD)

    Examples:
        GET /api/inventory-checks/?equipment=1&date_from=2025-01-01
    """
    queryset = InventoryCheck.objects.all()
    serializer_class = InventoryCheckSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return InventoryCheckListSerializer
        return InventoryCheckSerializer

    def get_queryset(self):
        """Get inventory checks with optional filtering."""
        queryset = InventoryCheck.objects.select_related('equipment', 'checked_by')

        # Equipment filter
        equipment = self.request.query_params.get('equipment', None)
        if equipment:
            queryset = queryset.filter(equipment_id=equipment)

        # Check type filter
        check_type = self.request.query_params.get('check_type', None)
        if check_type:
            queryset = queryset.filter(check_type=check_type)

        # Date filters
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        specific_date = self.request.query_params.get('date', None)

        if specific_date:
            try:
                specific_date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
                queryset = queryset.filter(check_date=specific_date_obj)
            except ValueError:
                pass

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(check_date__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(check_date__lte=date_to_obj)
            except ValueError:
                pass

        return queryset.order_by('-check_date')

    def perform_create(self, serializer):
        """Set performed_by when creating check."""
        serializer.save(performed_by=self.request.user)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export inventory checks to CSV file.

        Returns:
            CSV file download response

        Examples:
            GET /api/inventory-checks/export_csv/
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="tekshiruvlar.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Qurilma', 'Inventar raqami', 'Tekshiruv sanasi',
            'Tekshirgan', 'Joylashuv', 'Holat', 'Tekshiruv turi', 'Izoh'
        ])

        queryset = self.get_queryset()
        for check in queryset:
            writer.writerow([
                check.id,
                check.equipment.name,
                check.equipment.inventory_number,
                check.check_date,
                check.performed_by.username if check.performed_by else '',
                check.equipment.location or '',
                check.equipment.get_condition_display() if check.equipment.condition else '',
                check.get_check_type_display(),
                check.notes or ''
            ])

        return response


# ============================================
# Maintenance Record ViewSet
# ============================================

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Maintenance Record operations.

    Provides CRUD operations for maintenance records with filtering.

    Endpoints:
        - GET /api/maintenance/ - List all records
        - GET /api/maintenance/{id}/ - Get record details
        - POST /api/maintenance/ - Create new record
        - PUT /api/maintenance/{id}/ - Update record
        - DELETE /api/maintenance/{id}/ - Delete record
        - GET /api/maintenance/export_csv/ - Export to CSV

    Query Parameters:
        - equipment: Filter by equipment ID
        - type: Filter by maintenance type
        - status: Filter by status
        - priority: Filter by priority
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - date: Filter specific date (YYYY-MM-DD)

    Examples:
        GET /api/maintenance/?equipment=1&status=SCHEDULED
    """
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MaintenanceRecordListSerializer
        return MaintenanceRecordSerializer

    def get_queryset(self):
        """Get maintenance records with optional filtering."""
        queryset = MaintenanceRecord.objects.select_related('equipment', 'technician', 'created_by')

        # Equipment filter
        equipment = self.request.query_params.get('equipment', None)
        if equipment:
            queryset = queryset.filter(equipment_id=equipment)

        # Type filter
        maintenance_type = self.request.query_params.get('type', None)
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)

        # Status filter
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Priority filter
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)

        # Date filters
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        specific_date = self.request.query_params.get('date', None)

        if specific_date:
            try:
                specific_date_obj = datetime.strptime(specific_date, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_date=specific_date_obj)
            except ValueError:
                pass

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_date__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(scheduled_date__lte=date_to_obj)
            except ValueError:
                pass

        return queryset.order_by('-scheduled_date')

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export maintenance records to CSV file.

        Returns:
            CSV file download response

        Examples:
            GET /api/maintenance/export_csv/
        """
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="tamirlashlar.csv"'
        response.write('\ufeff')  # BOM for Excel UTF-8 support

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Qurilma', 'Inventar raqami', 'Ta\'mirlash turi',
            'Holat', 'Muhimlik', 'Tavsif', 'Rejalashtirilgan sana',
            'Taxminiy narx', 'Haqiqiy narx', 'Jami narx', 'Izoh'
        ])

        queryset = self.get_queryset()
        for record in queryset:
            writer.writerow([
                record.id,
                record.equipment.name,
                record.equipment.inventory_number,
                record.get_maintenance_type_display(),
                record.get_status_display(),
                record.get_priority_display(),
                record.description or '',
                record.scheduled_date or '',
                record.estimated_cost,
                record.actual_cost,
                record.get_total_cost(),
                record.notes or ''
            ])

        return response


# ============================================
# QR Scan ViewSet
# ============================================

class QRScanViewSet(viewsets.ViewSet):
    """
    ViewSet for QR code scanning.

    Provides endpoint to scan QR codes and retrieve equipment or employee data.

    Endpoints:
        - POST /api/qr-scan/scan/ - Scan QR code

    Request Body:
        - qr_data: QR code data string (EQUIPMENT:INV001 or EMPLOYEE:EMP001)

    Examples:
        POST /api/qr-scan/scan/
        {
            "qr_data": "EQUIPMENT:INV001"
        }
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """
        Scan QR code and retrieve comprehensive data.

        Supports equipment and employee QR codes with full details including
        branch information, assignments, and related data.

        Request Body:
            {
                "qr_data": "EQUIPMENT:INV001" or "EMPLOYEE:EMP001"
            }

        Returns:
            JSON with type and comprehensive data

        Examples:
            Equipment scan returns:
            {
                "type": "equipment",
                "data": {...equipment details...},
                "branch_info": {...branch details...},
                "current_assignment": {...assignment details...},
                "maintenance_history": [...recent maintenance...],
                "last_check": {...last inventory check...}
            }

            Employee scan returns:
            {
        """
        qr_data = request.data.get('qr_data', '')

        if not qr_data:
            return Response(
                {'error': 'QR kod ma\'lumoti yo\'q'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Strip whitespace from input
        qr_data = qr_data.strip()
        
        # Check if qr_data is a URL and extract the relevant part
        if '/equipment/' in qr_data:
            # Extract equipment inventory number from URL
            parts = qr_data.split('/equipment/')
            if len(parts) > 1:
                # Handle trailing slashes and query params
                inv_part = parts[1].split('?')[0].split('#')[0].strip().strip('/')
                qr_data = f"EQUIPMENT:{inv_part}"
        elif '/employee/' in qr_data:
            # Extract employee ID from URL
            parts = qr_data.split('/employee/')
            if len(parts) > 1:
                # Handle trailing slashes and query params
                emp_part = parts[1].split('?')[0].split('#')[0].strip().strip('/')
                qr_data = f"EMPLOYEE:{emp_part}"

        # Equipment QR code
        if qr_data.startswith('EQUIPMENT:'):
            inventory_number = qr_data.replace('EQUIPMENT:', '').strip()
            try:
                equipment = Equipment.objects.select_related(
                    'branch', 'category', 'branch__parent_branch'
                ).get(inventory_number=inventory_number)

                # Get maintenance history
                maintenance_history = MaintenanceService.get_equipment_maintenance_history(equipment)
                
                # Get current assignment
                current_assignment = None
                assignment_data = None
                
                # Use AssignmentService for consistency
                active_assignments = AssignmentService.get_active_assignments(equipment=equipment)
                if active_assignments.exists():
                     current_assignment = active_assignments.first()
                
                if current_assignment:
                    assignment_data = {
                        'employee_name': current_assignment.employee.get_full_name(),
                        'employee_id': current_assignment.employee.employee_id,
                        'assigned_date': current_assignment.assigned_date,
                        'expected_return_date': current_assignment.expected_return_date,
                        'department': current_assignment.employee.department.name if current_assignment.employee.department else None
                    }

                # Get last inventory check
                last_check = InventoryCheck.objects.filter(
                    equipment=equipment
                ).order_by('-check_date').first()

                return Response({
                    'type': 'equipment',
                    'data': {
                        'id': equipment.id,
                        'name': equipment.name,
                        'inventory_number': equipment.inventory_number,
                        'serial_number': equipment.serial_number,
                        'category_name': equipment.category.name if equipment.category else None,
                        'status': equipment.get_status_display(),
                        'condition': equipment.get_condition_display(),
                        'branch': equipment.branch.name,
                        'location': equipment.location,
                        'purchase_date': equipment.purchase_date,
                        'warranty_expiry': equipment.warranty_expiry,
                        'image': equipment.image.url if equipment.image else None,
                        'description': equipment.description or equipment.specifications
                    },
                    'current_assignment': assignment_data,
                    'maintenance_history_count': maintenance_history.count(),
                    'last_check_date': last_check.check_date if last_check else None
                })

            except Equipment.DoesNotExist:
                return Response(
                    {'error': 'Qurilma topilmadi'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Employee QR code
        elif qr_data.startswith('EMPLOYEE:'):
            employee_id = qr_data.replace('EMPLOYEE:', '').strip()
            try:
                # Use flexible lookup to help find the employee
                employee = Employee.objects.filter(employee_id__iexact=employee_id).select_related(
                    'branch', 'department', 'department__manager',
                    'branch__parent_branch'
                ).first()
                
                if not employee:
                     return Response(
                        {'error': 'Hodim topilmadi'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                department_info = None
                if employee.department:
                    department_info = {
                        'id': employee.department.id,
                        'code': employee.department.code,
                        'name': employee.department.name,
                        'location': employee.department.location,
                        'manager': employee.department.manager.get_full_name() if employee.department.manager else None,
                        'employee_count': employee.department.get_employee_count()
                    }

                # Get current assignments
                # Use AssignmentService and force evaluation
                current_assignments_qs = AssignmentService.get_active_assignments(employee=employee)
                current_assignments = list(current_assignments_qs)
                
                logger.error(f"DEBUG_QR_SCAN: QR Data: {qr_data}")
                logger.error(f"DEBUG_QR_SCAN: Extracted ID: {employee_id}")
                logger.error(f"DEBUG_QR_SCAN: Found Employee: {employee.get_full_name()} (PK: {employee.pk}, ID: {employee.employee_id})")
                logger.error(f"DEBUG_QR_SCAN: Query: {current_assignments_qs.query}")
                logger.error(f"DEBUG_QR_SCAN: Active assignments count: {len(current_assignments)}")
                
                equipment_list = [
                    {
                        'id': a.equipment.id,
                        'name': a.equipment.name,
                        'inventory_number': a.equipment.inventory_number,
                        'category': a.equipment.category.name if a.equipment.category else None,
                        'status': a.equipment.get_status_display(),
                        'condition': a.equipment.get_condition_display(),
                        'assigned_date': a.assigned_date,
                        'days_assigned': a.get_duration_days(),
                        'expected_return_date': a.expected_return_date,
                        'is_overdue': a.is_overdue()
                    }
                    for a in current_assignments
                ]

                # Get assignment statistics
                all_assignments = employee.assignments.all()
                total_assignments = all_assignments.count()
                returned_assignments = all_assignments.filter(return_date__isnull=False).count()
                
                assignment_stats = {
                    'total_assignments': total_assignments,
                    'current_assignments': len(current_assignments),
                    'returned_assignments': returned_assignments
                }

                # Check if is manager
                is_manager = False
                if employee.department:
                    is_manager = employee.department.manager == employee
                
                branch_info = {
                     'name': employee.branch.name,
                     'type': employee.branch.get_branch_type_display()
                }

                return Response({
                    'type': 'employee',
                    'data': {
                        'id': employee.id,
                        'full_name': employee.get_full_name(),
                        'employee_id': employee.employee_id,
                        'position': employee.position,
                        'email': employee.email,
                        'phone': employee.phone,
                        'hire_date': employee.hire_date,
                        'image': employee.image.url if hasattr(employee, 'image') and employee.image else None,
                        'is_manager': is_manager
                    },
                    'branch_info': branch_info,
                    'department_info': department_info,
                    'current_equipment': equipment_list,
                    'assignment_statistics': assignment_stats
                })
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Hodim topilmadi'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {'error': 'Noto\'g\'ri QR kod formati'},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================
# Audit Log ViewSet
# ============================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Audit Log (Read-Only).

    Provides read-only access to audit logs with filtering.

    Endpoints:
        - GET /api/audit-logs/ - List all logs
        - GET /api/audit-logs/{id}/ - Get log details

    Query Parameters:
        - user: Filter by user ID
        - action: Filter by action type
        - model: Filter by model name
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)

    Examples:
        GET /api/audit-logs/?user=1&action=CREATE&date_from=2025-01-01
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get audit logs with optional filtering."""
        queryset = AuditLog.objects.select_related('user').order_by('-timestamp')

        # User filter
        user = self.request.query_params.get('user', None)
        if user:
            queryset = queryset.filter(user_id=user)

        # Action filter
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)

        # Model filter
        model_name = self.request.query_params.get('model', None)
        if model_name:
            queryset = queryset.filter(model_name=model_name)

        # Date filters
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(timestamp__gte=date_from_obj)
            except ValueError:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(timestamp__lte=date_to_obj)
            except ValueError:
                pass

        return queryset[:100]  # Limit to 100 for performance


# ============================================
# OTP Authentication Views (Function-Based)
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_change_otp(request):
    """
    Request OTP for password change.

    Request Body:
        - email: User email address

    Returns:
        JSON with success message

    Examples:
        POST /api/auth/request-otp/
        {
            "email": "user@example.com"
        }
    """
    serializer = RequestPasswordChangeOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']

    try:
        user = User.objects.filter(email=email).first()
        if not user:
            # For security, still return success
            return Response({
                'message': 'Agar bu email bilan ro\'yxatdan o\'tgan bo\'lsangiz, OTP kod yuborildi.',
                'email': email,
                'expires_in_minutes': 10
            }, status=status.HTTP_200_OK)

        # Get IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Generate OTP
        otp = PasswordChangeOTP.generate_otp(user, ip_address)

        # Send email
        try:
            subject = 'Parol o\'zgartirish uchun OTP kod'
            message = f"""
Assalomu alaykum {user.username},

Siz parolingizni o'zgartirish uchun so'rov yubordingiz.

Tasdiqlash kodi: {otp.otp_code}

Bu kod 10 daqiqa davomida amal qiladi.

Agar siz bu so'rovni yubormaganingizda, bu emailni e'tiborsiz qoldiring.

Hurmat bilan,
Inventory Management System
            """

            from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False,
            )

            logger.info(f"OTP yuborildi: {user.username} ({email})")

            return Response({
                'message': 'OTP kod emailingizga yuborildi.',
                'email': email,
                'expires_in_minutes': 10
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Email yuborishda xatolik: {str(e)}", exc_info=True)
            otp.mark_as_used()
            return Response({
                'error': 'Email yuborishda xatolik yuz berdi.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unexpected error in request_password_change_otp: {str(e)}", exc_info=True)
        return Response({
            'error': 'Server xatosi.',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code.

    Request Body:
        - email: User email address
        - otp_code: OTP code

    Returns:
        JSON with verification result

    Examples:
        POST /api/auth/verify-otp/
        {
            "email": "user@example.com",
            "otp_code": "123456"
        }
    """
    serializer = VerifyOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']

    user = User.objects.filter(email=email).first()
    if not user:
        return Response(
            {'error': 'Foydalanuvchi topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verify OTP
    otp = PasswordChangeOTP.verify_otp(user, otp_code)

    if otp:
        return Response({
            'message': 'OTP kod to\'g\'ri',
            'verified': True
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Noto\'g\'ri yoki muddati o\'tgan OTP kod',
            'verified': False
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def change_password_with_otp(request):
    """
    Change password using OTP code.

    Request Body:
        - email: User email address
        - otp_code: OTP code
        - new_password: New password

    Returns:
        JSON with success message

    Examples:
        POST /api/auth/change-password-otp/
        {
            "email": "user@example.com",
            "otp_code": "123456",
            "new_password": "newpassword123"
        }
    """
    serializer = ChangePasswordWithOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']
    new_password = serializer.validated_data['new_password']

    user = User.objects.filter(email=email).first()
    if not user:
        return Response(
            {'error': 'Foydalanuvchi topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verify and mark OTP as used
    otp = PasswordChangeOTP.verify_otp(user, otp_code)

    if not otp:
        return Response(
            {'error': 'Noto\'g\'ri yoki muddati o\'tgan OTP kod'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Change password
    user.set_password(new_password)
    user.save()

    # Mark OTP as used
    otp.mark_as_used()

    # Audit log
    AuditLog.log_action(
        user=user,
        action=AuditAction.UPDATE,
        description='Parol OTP orqali o\'zgartirildi',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    logger.info(f"Parol OTP orqali o'zgartirildi: {user.username}")

    return Response({
        'message': 'Parol muvaffaqiyatli o\'zgartirildi',
        'success': True
    }, status=status.HTTP_200_OK)

