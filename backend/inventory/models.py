"""
Database models for Inventory Management System.

This module contains all database models for the inventory system.
Models are organized by domain and use base classes/mixins for code reuse.

Architecture:
    - Base models and mixins in base_models.py provide common functionality
    - Constants in constants.py define choices and validation rules
    - Validators in validators.py ensure data integrity
    - Utils in utils.py provide helper functions
"""

from datetime import date, timedelta
from typing import Optional

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from .base_models import (
    FullAuditModel, TimeStampedModel, QRCodeMixin,
    NoteMixin, CodeNameMixin, DescriptionMixin, LocationMixin
)
from .constants import (
    EquipmentStatus, EquipmentCondition, MaintenanceType,
    MaintenanceStatus, MaintenancePriority, CheckType,
    AuditAction, UploadPaths, BusinessConstants
)
from .validators import (
    validate_inventory_number, validate_employee_id, validate_phone_number,
    validate_passport_series, validate_serial_number, validate_positive_price,
    validate_depreciation_rate, validate_file_size, validate_image_extension
)
from .utils import (
    generate_equipment_qr_url, generate_employee_qr_url,
    calculate_depreciation, is_warranty_active, generate_otp_code,
    get_otp_expiry_time
)


# ============================================
# Branch Models
# ============================================

class Branch(CodeNameMixin, DescriptionMixin, FullAuditModel):
    """
    Branch/Filial of the organization.

    Represents physical branches/offices of the company in different locations.
    Each branch can have multiple departments, employees, and equipment.
    Supports hierarchical structure with parent-child relationships.

    Attributes:
        code: Unique branch code (from CodeNameMixin)
        name: Branch name (from CodeNameMixin)
        description: Branch description (from DescriptionMixin)

        Location Information:
        address: Full physical address
        city: City name
        region: Region/Province
        country: Country name
        postal_code: Postal/ZIP code
        phone: Branch phone number
        email: Branch email address

        Hierarchy:
        parent_branch: Parent branch (for hierarchical structure)
        branch_type: Type of branch (HEADQUARTERS, REGIONAL, LOCAL)

        Management:
        manager: Employee managing this branch
        area_manager: Area manager overseeing multiple branches

        Additional:
        timezone: Branch timezone for scheduling
        is_warehouse: Whether this branch has warehouse
        is_retail: Whether this branch has retail operations
        opening_date: When branch was opened
        closing_date: When branch was closed (if applicable)
        is_active: Whether branch is currently operational (from FullAuditModel)

    Relationships:
        departments: Departments in this branch (reverse FK)
        employees: Employees in this branch (reverse FK)
        equipments: Equipment in this branch (reverse FK)
        sub_branches: Child branches (reverse FK to parent_branch)

    Example:
        branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Central Office",
            address="Amir Temur 107A",
            city="Tashkent",
            region="Tashkent",
            country="Uzbekistan",
            branch_type="HEADQUARTERS"
        )
    """
    # Branch Types
    HEADQUARTERS = 'HEADQUARTERS'
    REGIONAL = 'REGIONAL'
    LOCAL = 'LOCAL'
    WAREHOUSE = 'WAREHOUSE'

    BRANCH_TYPE_CHOICES = (
        (HEADQUARTERS, 'Bosh ofis'),
        (REGIONAL, 'Mintaqaviy filial'),
        (LOCAL, 'Mahalliy filial'),
        (WAREHOUSE, 'Ombor'),
    )

    # Location Information
    address = models.CharField(
        max_length=500,
        verbose_name="Manzil",
        help_text="To'liq manzil"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Shahar",
        help_text="Shahar nomi"
    )
    region = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Viloyat/Mintaqa",
        help_text="Viloyat yoki mintaqa"
    )
    country = models.CharField(
        max_length=100,
        default='Uzbekistan',
        verbose_name="Davlat",
        help_text="Davlat nomi"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Pochta indeksi",
        help_text="Pochta indeksi"
    )

    # Contact Information
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon",
        help_text="Filial telefon raqami",
        validators=[validate_phone_number]
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email",
        help_text="Filial email manzili"
    )

    # Hierarchy
    parent_branch = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_branches',
        verbose_name="Asosiy filial",
        help_text="Yuqori darajadagi filial (ierarxiya uchun)"
    )
    branch_type = models.CharField(
        max_length=20,
        choices=BRANCH_TYPE_CHOICES,
        default=LOCAL,
        verbose_name="Filial turi",
        help_text="Filialning turi",
        db_index=True
    )

    # Management
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        verbose_name="Filial menejeri",
        help_text="Filialni boshqaruvchi xodim"
    )
    area_manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='area_managed_branches',
        verbose_name="Hudud menejeri",
        help_text="Bir nechta filialni nazorat qiluvchi menejer"
    )

    # Additional Information
    timezone = models.CharField(
        max_length=50,
        default='Asia/Tashkent',
        verbose_name="Vaqt mintaqasi",
        help_text="Filialning vaqt mintaqasi"
    )
    is_warehouse = models.BooleanField(
        default=False,
        verbose_name="Ombor",
        help_text="Bu filial ombor funktsiyasiga egami"
    )
    is_retail = models.BooleanField(
        default=False,
        verbose_name="Chakana savdo",
        help_text="Bu filial chakana savdo bilan shug'ullanadimi"
    )
    opening_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ochilgan sana",
        help_text="Filial ochilgan sana"
    )
    closing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Yopilgan sana",
        help_text="Filial yopilgan sana (agar yopilgan bo'lsa)"
    )

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['city']),
            models.Index(fields=['branch_type']),
            models.Index(fields=['parent_branch']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        """String representation of branch."""
        return f"{self.name} ({self.city})"

    def get_full_address(self) -> str:
        """
        Get complete formatted address.

        Returns:
            Formatted full address string

        Example:
            >>> branch.get_full_address()
            'Amir Temur 107A, Tashkent, Tashkent, Uzbekistan'
        """
        parts = [self.address, self.city]
        if self.region:
            parts.append(self.region)
        parts.append(self.country)
        return ', '.join(parts)

    def get_employee_count(self) -> int:
        """
        Get total number of active employees in this branch.

        Returns:
            Count of active employees

        Example:
            >>> branch.get_employee_count()
            45
        """
        return self.employees.filter(is_active=True).count()

    def get_equipment_count(self) -> int:
        """
        Get total number of active equipment in this branch.

        Returns:
            Count of active equipment

        Example:
            >>> branch.get_equipment_count()
            120
        """
        return self.equipments.filter(is_active=True).count()

    def get_department_count(self) -> int:
        """
        Get number of active departments in this branch.

        Returns:
            Count of active departments

        Example:
            >>> branch.get_department_count()
            8
        """
        return self.departments.filter(is_active=True).count()

    def get_all_sub_branches(self, _visited=None) -> list:
        """
        Get all sub-branches recursively (entire hierarchy below this branch).

        Returns:
            List of all descendant branches

        Example:
            >>> headquarters = Branch.objects.get(branch_type='HEADQUARTERS')
            >>> all_branches = headquarters.get_all_sub_branches()
            >>> len(all_branches)
            15
        """
        if _visited is None:
            _visited = set()
        if self.pk in _visited:
            return []
        _visited.add(self.pk)

        children = list(self.sub_branches.filter(is_active=True))
        sub_branches = list(children)
        for sub_branch in children:
            sub_branches.extend(sub_branch.get_all_sub_branches(_visited=_visited))
        return sub_branches

    def get_hierarchy_level(self) -> int:
        """
        Get hierarchy level (0 for top-level, 1 for first child, etc.).

        Returns:
            Hierarchy level as integer

        Example:
            >>> branch.get_hierarchy_level()
            2
        """
        level = 0
        current = self
        visited = set()
        while current.parent_branch:
            if current.pk in visited:
                break
            visited.add(current.pk)
            level += 1
            current = current.parent_branch
        return level

    def is_operational(self) -> bool:
        """
        Check if branch is currently operational.

        Branch is operational if active and not closed.

        Returns:
            True if operational, False otherwise

        Example:
            >>> if branch.is_operational():
            ...     print("Branch is open for business")
        """
        if not self.is_active:
            return False
        if self.closing_date and self.closing_date <= date.today():
            return False
        return True


# ============================================
# Department Models
# ============================================

class Department(CodeNameMixin, DescriptionMixin, FullAuditModel):
    """
    Department/Division within the organization.

    Represents organizational units that contain employees and equipment.
    Supports hierarchical structure through optional manager relationship.

    Attributes:
        code: Unique department code (from CodeNameMixin)
        name: Department name (from CodeNameMixin)
        description: Department description (from DescriptionMixin)
        location: Physical location of the department
        manager: Employee managing this department (optional)
        is_active: Whether department is currently active (from FullAuditModel)
        created_at: Creation timestamp (from FullAuditModel)
        updated_at: Last update timestamp (from FullAuditModel)
        created_by: User who created this department (from FullAuditModel)

    Relationships:
        employees: Employees in this department (reverse FK)
        managed_departments: If this department has a manager

    Example:
        dept = Department.objects.create(
            code="IT",
            name="Information Technology",
            description="IT Department",
            location="Building A, Floor 3"
        )
    """
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name="Filial",
        help_text="Bo'lim qaysi filialga tegishli"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Joylashuv",
        help_text="Bo'limning joylashuvi"
    )
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name="Menejer",
        help_text="Bo'lim menejeri (ixtiyoriy)"
    )

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def get_employee_count(self) -> int:
        """
        Get count of active employees in this department.

        Returns:
            Number of active employees

        Example:
            >>> dept.get_employee_count()
            15
        """
        return self.employees.filter(is_active=True).count()

    def get_equipment_count(self) -> int:
        """
        Get count of equipment assigned to this department's employees.

        Returns:
            Number of equipment items

        Example:
            >>> dept.get_equipment_count()
            45
        """
        return Assignment.objects.filter(
            employee__department=self,
            return_date__isnull=True
        ).count()


# ============================================
# Employee Models
# ============================================

class Employee(QRCodeMixin, NoteMixin, FullAuditModel):
    """
    Employee/Staff member in the organization.

    Represents employees who can be assigned equipment.
    Includes personal information, employment details, and contact information.

    Attributes:
        employee_id: Unique employee identifier
        first_name: Employee's first name
        last_name: Employee's last name
        middle_name: Employee's middle name (optional)
        department: Department the employee belongs to
        position: Job position/title
        email: Email address (unique, optional)
        phone: Phone number (optional)
        hire_date: Date when employee was hired
        termination_date: Date when employee left (if applicable)
        birth_date: Employee's birth date (optional)
        address: Residential address (optional)
        passport_series: Passport number (optional)
        emergency_contact: Emergency contact name (optional)
        emergency_phone: Emergency contact phone (optional)
        qr_code: QR code for quick access (from QRCodeMixin)
        notes: Additional notes (from NoteMixin)
        is_active: Whether employee is currently active (from FullAuditModel)

    Relationships:
        assignments: Equipment assignments (reverse FK)
        managed_departments: Departments managed by this employee (reverse FK)

    Example:
        employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            department=dept,
            position="Software Engineer",
            email="john.doe@company.com"
        )
    """
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Filial",
        help_text="Hodim qaysi filialda ishlaydi"
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Ism",
        help_text="Hodimning ismi"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Familiya",
        help_text="Hodimning familiyasi"
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Otasining ismi",
        help_text="Otasining ismi (ixtiyoriy)"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name="Bo'lim",
        help_text="Hodim ishlayotgan bo'lim"
    )
    position = models.CharField(
        max_length=100,
        verbose_name="Lavozim",
        help_text="Hodimning lavozimi"
    )
    email = models.EmailField(
        blank=True,
        unique=True,
        null=True,
        verbose_name="Email",
        help_text="Email manzil (ixtiyoriy)"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefon",
        help_text="Telefon raqam (ixtiyoriy)",
        validators=[validate_phone_number]
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Hodim ID",
        help_text="Noyob hodim identifikatori",
        validators=[validate_employee_id],
        db_index=True
    )

    # Override QRCodeMixin qr_code to set specific upload path
    qr_code = models.ImageField(
        upload_to=UploadPaths.QR_CODE_EMPLOYEE,
        blank=True,
        null=True,
        verbose_name="QR Kod",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )

    hire_date = models.DateField(
        verbose_name="Ishga qabul qilingan sana",
        null=True,
        blank=True,
        help_text="Hodim ishga qabul qilingan sana"
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ishdan chiqqan sana",
        help_text="Hodim ishdan chiqqan sana (agar mavjud bo'lsa)"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tug'ilgan sana",
        help_text="Hodimning tug'ilgan sanasi"
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name="Manzil",
        help_text="Yashash manzili"
    )
    passport_series = models.CharField(
        null=True,
        max_length=9,
        blank=True,
        verbose_name="Pasport seriyasi",
        help_text="Pasport seriyasi (XX1234567 formatida)",
        validators=[validate_passport_series]
    )
    emergency_contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Favqulodda aloqa",
        help_text="Favqulodda vaziyat uchun aloqa qilinadigan shaxs"
    )
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Favqulodda telefon",
        help_text="Favqulodda vaziyat uchun telefon raqam"
    )

    class Meta:
        verbose_name = "Hodim"
        verbose_name_plural = "Hodimlar"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['department', 'is_active']),
        ]

    def __str__(self) -> str:
        """String representation of employee."""
        return f"{self.last_name} {self.first_name} ({self.position})"

    def get_full_name(self) -> str:
        """
        Get employee's full name including middle name if available.

        Returns:
            Full name string

        Example:
            >>> employee.get_full_name()
            'John Michael Doe'
        """
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def get_current_equipment_count(self) -> int:
        """
        Get count of equipment currently assigned to this employee.

        Returns:
            Number of assigned equipment items

        Example:
            >>> employee.get_current_equipment_count()
            3
        """
        return self.assignments.filter(return_date__isnull=True).count()

    def get_qr_code_data(self) -> str:
        """
        Get data for QR code generation.

        Returns:
            URL for employee detail page

        Example:
            >>> employee.get_qr_code_data()
            'http://localhost:3000/employee/EMP001'
        """
        return generate_employee_qr_url(self.employee_id)

    def save(self, *args, **kwargs):
        """
        Override save to generate QR code if not exists.

        Automatically generates QR code on first save.
        """
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)


# ============================================
# Equipment Category Models
# ============================================

class EquipmentCategory(CodeNameMixin, DescriptionMixin, TimeStampedModel):
    """
    Equipment category/classification.

    Hierarchical categorization system for equipment.
    Supports parent-child relationships for subcategories.

    Attributes:
        code: Unique category code (from CodeNameMixin)
        name: Category name (from CodeNameMixin)
        description: Category description (from DescriptionMixin)
        parent: Parent category for hierarchical structure (optional)
        is_active: Whether category is currently active

    Relationships:
        subcategories: Child categories (reverse FK)
        equipments: Equipment in this category (reverse FK)

    Example:
        parent = EquipmentCategory.objects.create(
            code="COMP",
            name="Computers"
        )
        child = EquipmentCategory.objects.create(
            code="LAPTOP",
            name="Laptops",
            parent=parent
        )
    """
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Asosiy kategoriya",
        help_text="Yuqori darajali kategoriya (ixtiyoriy)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol",
        help_text="Kategoriya faolmi"
    )

    class Meta:
        verbose_name = "Qurilma kategoriyasi"
        verbose_name_plural = "Qurilma kategoriyalari"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
        ]

    def get_equipment_count(self) -> int:
        """
        Get count of equipment in this category.

        Returns:
            Number of equipment items

        Example:
            >>> category.get_equipment_count()
            25
        """
        return self.equipments.count()

    def get_all_subcategories(self):
        """
        Get all subcategories recursively.

        Returns:
            QuerySet of all subcategories

        Example:
            >>> category.get_all_subcategories()
            <QuerySet [<EquipmentCategory: Laptops>, <EquipmentCategory: Desktops>]>
        """
        subcats = list(self.subcategories.all())
        for subcat in self.subcategories.all():
            subcats.extend(subcat.get_all_subcategories())
        return subcats


# ============================================
# Equipment Models
# ============================================

class Equipment(QRCodeMixin, NoteMixin, LocationMixin, FullAuditModel):
    """
    Equipment/Asset in the inventory system.

    Represents physical equipment/assets that can be assigned to employees.
    Tracks financial information, warranty, status, and condition.

    Attributes:
        inventory_number: Unique inventory identifier
        name: Equipment name/description
        category: Equipment category (FK to EquipmentCategory)
        serial_number: Manufacturer serial number (optional)
        manufacturer: Manufacturer/brand name (optional)
        model: Model name/number (optional)
        specifications: JSON field for technical specifications (optional)

        Financial:
        purchase_date: Date when equipment was purchased (optional)
        purchase_price: Original purchase price
        depreciation_rate: Annual depreciation percentage
        current_value: Current depreciated value

        Warranty:
        warranty_expiry: Warranty expiration date (optional)
        warranty_provider: Warranty provider name (optional)

        Status and Condition:
        status: Current status (AVAILABLE, ASSIGNED, etc.)
        condition: Physical condition (NEW, EXCELLENT, etc.)

        Additional:
        barcode: Barcode for scanning (optional)
        image: Equipment photo (optional)
        is_critical: Whether equipment is mission-critical
        requires_training: Whether special training is required
        qr_code: QR code for quick access (from QRCodeMixin)
        notes: Additional notes (from NoteMixin)
        location/default_location: Location tracking (from LocationMixin)

    Relationships:
        assignments: Assignment history (reverse FK)
        inventory_checks: Inventory check history (reverse FK)
        maintenance_records: Maintenance history (reverse FK)

    Example:
        equipment = Equipment.objects.create(
            inventory_number="INV001",
            name="Dell Laptop XPS 15",
            category=laptop_category,
            serial_number="ABC123456",
            purchase_price=1500.00,
            status=EquipmentStatus.AVAILABLE
        )
    """
    # Basic Information
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='equipments',
        verbose_name="Filial",
        help_text="Qurilma qaysi filialda joylashgan"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Qurilma nomi",
        help_text="Qurilmaning to'liq nomi"
    )
    category = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equipments',
        verbose_name="Kategoriya",
        help_text="Qurilma kategoriyasi"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Seriya raqami",
        help_text="Ishlab chiqaruvchi seriya raqami",
        validators=[validate_serial_number]
    )
    inventory_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Inventar raqami",
        help_text="Noyob inventar identifikatori",
        validators=[validate_inventory_number],
        db_index=True
    )
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ishlab chiqaruvchi",
        help_text="Ishlab chiqaruvchi kompaniya nomi"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Model",
        help_text="Model nomi/raqami"
    )
    specifications = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Texnik xususiyatlar",
        help_text="Texnik xususiyatlar JSON formatda"
    )

    # Financial Information
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Xarid qilingan sana",
        help_text="Qurilma sotib olingan sana"
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Xarid narxi",
        help_text="Dastlabki xarid narxi",
        validators=[validate_positive_price]
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Amortizatsiya foizi",
        help_text="Yillik amortizatsiya foizi (0-100)",
        validators=[validate_depreciation_rate]
    )
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Joriy qiymati",
        help_text="Amortizatsiya hisobga olingan joriy qiymat",
        validators=[validate_positive_price]
    )

    # Warranty Information
    warranty_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kafolat muddati",
        help_text="Kafolat tugash sanasi"
    )
    warranty_provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kafolat beruvchi",
        help_text="Kafolat beruvchi kompaniya"
    )

    # Status and Condition
    status = models.CharField(
        max_length=20,
        choices=EquipmentStatus.CHOICES,
        default=EquipmentStatus.AVAILABLE,
        verbose_name="Holati",
        help_text="Qurilmaning joriy holati",
        db_index=True
    )
    condition = models.CharField(
        max_length=20,
        choices=EquipmentCondition.CHOICES,
        default=EquipmentCondition.GOOD,
        verbose_name="Fizik holati",
        help_text="Qurilmaning fizik holati"
    )

    # Media Files
    qr_code = models.ImageField(
        upload_to=UploadPaths.QR_CODE_EQUIPMENT,
        blank=True,
        null=True,
        verbose_name="QR Kod",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )
    image = models.ImageField(
        upload_to=UploadPaths.EQUIPMENT_IMAGES,
        blank=True,
        null=True,
        verbose_name="Rasm",
        help_text="Qurilma rasmi",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_file_size]
    )

    # Additional Fields
    barcode = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        verbose_name="Barcode",
        help_text="Barcode identifikatori"
    )
    is_critical = models.BooleanField(
        default=False,
        verbose_name="Muhim qurilma",
        help_text="Muhim/kritik qurilma ekanligini belgilaydi"
    )
    requires_training = models.BooleanField(
        default=False,
        verbose_name="Treningni talab qiladi",
        help_text="Foydalanish uchun maxsus trening kerakmi"
    )

    class Meta:
        verbose_name = "Qurilma"
        verbose_name_plural = "Qurilmalar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_number']),
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['warranty_expiry']),
        ]

    def __str__(self) -> str:
        """String representation of equipment."""
        return f"{self.name} ({self.inventory_number})"

    def get_current_assignment(self) -> Optional['Assignment']:
        """
        Get current active assignment for this equipment.

        Returns:
            Assignment object if currently assigned, None otherwise

        Example:
            >>> assignment = equipment.get_current_assignment()
            >>> if assignment:
            ...     print(f"Assigned to: {assignment.employee}")
        """
        return self.assignments.filter(return_date__isnull=True).first()

    def get_last_inventory_check(self) -> Optional['InventoryCheck']:
        """
        Get most recent inventory check for this equipment.

        Returns:
            Most recent InventoryCheck object or None

        Example:
            >>> check = equipment.get_last_inventory_check()
            >>> if check:
            ...     print(f"Last checked: {check.check_date}")
        """
        return self.inventory_checks.order_by('-check_date').first()

    def calculate_current_value(self) -> float:
        """
        Calculate current value based on depreciation.

        Uses straight-line depreciation method.
        Updates the current_value field but doesn't save automatically.

        Returns:
            Calculated current value

        Example:
            >>> value = equipment.calculate_current_value()
            >>> equipment.current_value
            750.00
        """
        if self.purchase_date and self.purchase_price and self.depreciation_rate:
            self.current_value = calculate_depreciation(
                self.purchase_price,
                self.purchase_date,
                self.depreciation_rate
            )
            return float(self.current_value)
        return float(self.purchase_price)

    def is_warranty_active(self) -> bool:
        """
        Check if warranty is still active.

        Returns:
            True if warranty is active, False otherwise

        Example:
            >>> if equipment.is_warranty_active():
            ...     print("Still under warranty!")
        """
        return is_warranty_active(self.warranty_expiry)

    def is_available_for_assignment(self) -> bool:
        """
        Check if equipment can be assigned.

        Equipment can be assigned if status is AVAILABLE or MAINTENANCE
        and it's not currently assigned.

        Returns:
            True if available for assignment, False otherwise

        Example:
            >>> if equipment.is_available_for_assignment():
            ...     assignment = Assignment.objects.create(...)
        """
        return (
            self.status in [EquipmentStatus.AVAILABLE, EquipmentStatus.MAINTENANCE]
            and not self.get_current_assignment()
            and self.is_active
        )

    def get_qr_code_data(self) -> str:
        """
        Get data for QR code generation.

        Returns:
            URL for equipment detail page

        Example:
            >>> equipment.get_qr_code_data()
            'http://localhost:3000/equipment/INV001'
        """
        return generate_equipment_qr_url(self.inventory_number)

    def save(self, *args, **kwargs):
        """
        Override save to generate QR code and calculate depreciation.

        Automatically:
        - Generates QR code on first save
        - Calculates current value if not set
        """
        if not self.qr_code:
            self.generate_qr_code()

        if not self.current_value or self.current_value == 0:
            self.calculate_current_value()

        super().save(*args, **kwargs)


# ============================================
# Assignment Models
# ============================================

class Assignment(NoteMixin, TimeStampedModel):
    """
    Equipment assignment to an employee.

    Tracks when equipment is assigned to employees and returned.
    Includes condition tracking and approval workflow.

    Attributes:
        equipment: Equipment being assigned (FK)
        employee: Employee receiving equipment (FK)
        assigned_date: When equipment was assigned (auto-set)
        expected_return_date: Expected return date (optional)
        return_date: Actual return date (null if still assigned)

        Condition Tracking:
        condition_on_assignment: Equipment condition when assigned
        condition_on_return: Equipment condition when returned

        Workflow:
        purpose: Purpose/reason for assignment
        location: Where equipment will be used
        is_temporary: Whether this is a temporary assignment
        requires_approval: Whether approval is needed
        is_approved: Whether assignment is approved

        Documentation:
        acknowledgement_signature: Employee signature image (optional)
        notes: Assignment notes (from NoteMixin)
        return_notes: Return notes

        Audit:
        assigned_by: User who created assignment
        returned_by: User who processed return
        approved_by: User who approved assignment

    Relationships:
        equipment: Equipment being assigned
        employee: Employee receiving equipment

    Example:
        assignment = Assignment.objects.create(
            equipment=laptop,
            employee=john,
            purpose="Work from home setup",
            condition_on_assignment="Excellent condition",
            assigned_by=request.user
        )
    """
    # Core Fields
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Qurilma",
        help_text="Tayinlanayotgan qurilma"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name="Hodim",
        help_text="Qurilma tayinlanayotgan hodim"
    )

    # Date Fields
    assigned_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Tayinlangan sana",
        help_text="Qurilma tayinlangan vaqt",
        db_index=True
    )
    expected_return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Qaytarish rejalashtirilgan sana",
        help_text="Qurilmani qaytarish kerak bo'lgan sana"
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Qaytarilgan sana",
        help_text="Qurilma qaytarilgan vaqt",
        db_index=True
    )

    # Condition Tracking
    condition_on_assignment = models.TextField(
        blank=True,
        verbose_name="Tayinlash paytidagi holat",
        help_text="Qurilmaning tayinlash paytidagi holati"
    )
    condition_on_return = models.TextField(
        blank=True,
        null=True,
        verbose_name="Qaytarish paytidagi holat",
        help_text="Qurilmaning qaytarish paytidagi holati"
    )

    # Assignment Details
    purpose = models.TextField(
        blank=True,
        verbose_name="Foydalanish maqsadi",
        help_text="Qurilma nima uchun tayinlanmoqda"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Joylashuv",
        help_text="Qurilma qayerda foydalaniladi"
    )
    is_temporary = models.BooleanField(
        default=False,
        verbose_name="Vaqtinchalik",
        help_text="Vaqtinchalik tayinlash"
    )

    # Approval Workflow
    requires_approval = models.BooleanField(
        default=False,
        verbose_name="Tasdiqlash kerak",
        help_text="Tasdiqlash talab qilinadimi"
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Tasdiqlangan",
        help_text="Tayinlash tasdiqlangan"
    )

    # Documentation
    return_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Qaytarish izohlari",
        help_text="Qurilma qaytarilganda qo'shilgan izohlar"
    )
    acknowledgement_signature = models.ImageField(
        upload_to=UploadPaths.SIGNATURES,
        blank=True,
        null=True,
        verbose_name="Hodim imzosi",
        help_text="Hodimning qabul qilish imzosi"
    )

    # Audit Fields
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_created',
        verbose_name="Tayinlagan",
        help_text="Tayinlashni amalga oshirgan foydalanuvchi"
    )
    returned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments_returned',
        verbose_name="Qabul qilgan",
        help_text="Qaytarishni qabul qilgan foydalanuvchi"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments_approved',
        verbose_name="Tasdiqlagan",
        help_text="Tayinlashni tasdiqlagan foydalanuvchi"
    )

    class Meta:
        verbose_name = "Tayinlash"
        verbose_name_plural = "Tayinlashlar"
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['employee', 'return_date']),
            models.Index(fields=['equipment', 'return_date']),
            models.Index(fields=['assigned_date']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self) -> str:
        """String representation of assignment."""
        return f"{self.equipment.name} -> {self.employee.get_full_name()}"

    def get_duration_days(self) -> int:
        """
        Calculate assignment duration in days.

        Returns days from assignment to return (or current date if not returned).

        Returns:
            Number of days

        Example:
            >>> assignment.get_duration_days()
            45
        """
        if self.return_date:
            return (self.return_date - self.assigned_date).days
        return (timezone.now() - self.assigned_date).days

    def is_overdue(self) -> bool:
        """
        Check if assignment is past expected return date.

        Returns:
            True if overdue, False otherwise

        Example:
            >>> if assignment.is_overdue():
            ...     send_reminder_email()
        """
        if self.expected_return_date and not self.return_date:
            return date.today() > self.expected_return_date
        return False

    def is_active(self) -> bool:
        """
        Check if assignment is currently active (not returned).

        Returns:
            True if active, False if returned

        Example:
            >>> assignment.is_active()
            True
        """
        return self.return_date is None

    def mark_returned(self, user=None, condition='', notes=''):
        """
        Mark assignment as returned.

        Args:
            user: User processing the return
            condition: Equipment condition on return
            notes: Return notes

        Example:
            >>> assignment.mark_returned(
            ...     user=request.user,
            ...     condition="Good condition",
            ...     notes="All accessories included"
            ... )
        """
        self.return_date = timezone.now()
        self.returned_by = user
        self.condition_on_return = condition
        if notes:
            self.return_notes = notes
        self.equipment.status = EquipmentStatus.AVAILABLE
        self.equipment.save()
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save to update equipment status.

        Automatically updates equipment status based on assignment state.
        Uses update() to avoid triggering Equipment.save() override recursively.
        """
        if self.return_date:
            new_status = EquipmentStatus.AVAILABLE
        else:
            new_status = EquipmentStatus.ASSIGNED

        if self.equipment.status != new_status:
            Equipment.objects.filter(pk=self.equipment.pk).update(status=new_status)
            self.equipment.status = new_status

        super().save(*args, **kwargs)


# ============================================
# Inventory Check Models
# ============================================

class InventoryCheck(NoteMixin, TimeStampedModel):
    """
    Inventory verification/audit check.

    Records periodic checks of equipment location and condition.
    Supports different check types and employee confirmation.

    Attributes:
        equipment: Equipment being checked (FK)
        check_date: When check was performed (auto-set)
        check_type: Type of check (SCHEDULED, RANDOM, etc.)
        checked_by: User who performed check

        Location Verification:
        location: Actual location found
        expected_location: Expected location
        location_mismatch: Whether location didn't match

        Condition Assessment:
        condition: Text description of condition
        physical_condition: Structured condition rating
        is_functional: Whether equipment is working

        Issues:
        issues_found: Description of any issues
        requires_maintenance: Whether maintenance is needed
        requires_replacement: Whether replacement is needed

        Confirmation:
        employee_confirmed: Whether employee confirmed check
        employee: Employee who confirmed (optional)
        confirmation_date: When confirmation happened

        Additional:
        photos: Photos taken during check (optional)
        next_check_date: When next check should occur
        notes: Check notes (from NoteMixin)

    Example:
        check = InventoryCheck.objects.create(
            equipment=laptop,
            check_type=CheckType.SCHEDULED,
            location="Office 201",
            condition="Good working order",
            is_functional=True,
            checked_by=request.user
        )
    """
    # Core Fields
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='inventory_checks',
        verbose_name="Qurilma",
        help_text="Tekshirilayotgan qurilma"
    )
    check_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Tekshirilgan sana",
        help_text="Tekshiruv amalga oshirilgan vaqt",
        db_index=True
    )
    check_type = models.CharField(
        max_length=20,
        choices=CheckType.CHOICES,
        default=CheckType.SCHEDULED,
        verbose_name="Tekshiruv turi",
        help_text="Tekshiruv turi"
    )
    checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_checks_performed',
        verbose_name="Tekshirgan",
        help_text="Tekshiruvni amalga oshirgan foydalanuvchi"
    )

    # Location Verification
    location = models.CharField(
        max_length=200,
        verbose_name="Joylashuv",
        help_text="Qurilma topilgan joylashuv"
    )
    expected_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kutilgan joylashuv",
        help_text="Qurilma bo'lishi kerak bo'lgan joylashuv"
    )
    location_mismatch = models.BooleanField(
        default=False,
        verbose_name="Joylashuv mos kelmadi",
        help_text="Haqiqiy va kutilgan joylashuv mos kelmaganmi"
    )

    # Condition Assessment
    condition = models.TextField(
        verbose_name="Holat",
        help_text="Qurilma holatining batafsil tavsifi"
    )
    physical_condition = models.CharField(
        max_length=20,
        choices=EquipmentCondition.CHOICES,
        default=EquipmentCondition.GOOD,
        verbose_name="Fizik holat",
        help_text="Fizik holatning baholangan darajasi"
    )
    is_functional = models.BooleanField(
        default=True,
        verbose_name="Ishlayaptimi",
        help_text="Qurilma to'g'ri ishlayaptimi"
    )

    # Issues and Maintenance
    issues_found = models.TextField(
        blank=True,
        verbose_name="Topilgan muammolar",
        help_text="Tekshiruv davomida topilgan muammolar"
    )
    requires_maintenance = models.BooleanField(
        default=False,
        verbose_name="Ta'mirlash kerak",
        help_text="Qurilma ta'mirlashni talab qiladimi"
    )
    requires_replacement = models.BooleanField(
        default=False,
        verbose_name="Almashtirish kerak",
        help_text="Qurilma almashtirishni talab qiladimi"
    )

    # Employee Confirmation
    employee_confirmed = models.BooleanField(
        default=False,
        verbose_name="Hodim tasdiqladi",
        help_text="Hodim tekshiruvni tasdiqladimi"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_checks',
        verbose_name="Tasdiqlagan hodim",
        help_text="Tekshiruvni tasdiqlagan hodim"
    )
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Tasdiqlangan vaqt",
        help_text="Hodim tomonidan tasdiqlangan vaqt"
    )

    # Additional
    photos = models.ImageField(
        upload_to=UploadPaths.INVENTORY_CHECK_PHOTOS,
        blank=True,
        null=True,
        verbose_name="Fotosuratlar",
        help_text="Tekshiruv davomida olingan fotosuratlar"
    )
    next_check_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Keyingi tekshiruv sanasi",
        help_text="Keyingi tekshiruv rejalashtirilgan sana"
    )

    class Meta:
        verbose_name = "Inventarizatsiya tekshiruvi"
        verbose_name_plural = "Inventarizatsiya tekshiruvlari"
        ordering = ['-check_date']
        indexes = [
            models.Index(fields=['equipment', 'check_date']),
            models.Index(fields=['checked_by', 'check_date']),
            models.Index(fields=['check_type']),
            models.Index(fields=['requires_maintenance']),
        ]

    def __str__(self) -> str:
        """String representation of inventory check."""
        return f"{self.equipment.name} - {self.check_date.strftime('%Y-%m-%d %H:%M')}"

    def mark_employee_confirmed(self, employee, confirmation_date=None):
        """
        Mark this check as confirmed by employee.

        Args:
            employee: Employee confirming the check
            confirmation_date: Confirmation datetime (defaults to now)

        Example:
            >>> check.mark_employee_confirmed(employee=john)
        """
        self.employee_confirmed = True
        self.employee = employee
        self.confirmation_date = confirmation_date or timezone.now()
        self.save()


# ============================================
# Maintenance Record Models
# ============================================

class MaintenanceRecord(NoteMixin, TimeStampedModel):
    """
    Equipment maintenance and repair record.

    Tracks maintenance activities including repairs, upgrades, and inspections.
    Includes cost tracking and scheduling.

    Attributes:
        equipment: Equipment being maintained (FK)
        maintenance_type: Type of maintenance (REPAIR, UPGRADE, etc.)
        status: Current status (SCHEDULED, IN_PROGRESS, etc.)
        priority: Priority level (LOW, MEDIUM, HIGH, CRITICAL)

        Schedule:
        scheduled_date: When maintenance is scheduled
        started_date: When work actually started
        performed_date: When work was completed
        next_maintenance_date: When next maintenance is due

        Work Description:
        description: What needs to be done
        problem_found: Problem discovered
        solution_applied: Solution implemented
        parts_replaced: Parts that were replaced

        Personnel:
        performed_by: Who did the work (text)
        technician: Employee who performed work (FK)
        vendor: External vendor name

        Costs:
        estimated_cost: Estimated total cost
        actual_cost: Actual total cost
        labor_cost: Labor cost component
        parts_cost: Parts cost component

        Additional:
        downtime_hours: Equipment downtime duration
        warranty_claim: Whether this was warranty work
        preventive: Whether this was preventive maintenance
        attachments: Supporting documents
        notes: Maintenance notes (from NoteMixin)

    Example:
        maintenance = MaintenanceRecord.objects.create(
            equipment=printer,
            maintenance_type=MaintenanceType.REPAIR,
            status=MaintenanceStatus.SCHEDULED,
            priority=MaintenancePriority.HIGH,
            description="Replace drum unit",
            estimated_cost=150.00
        )
    """
    # Core Fields
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_records',
        verbose_name="Qurilma",
        help_text="Ta'mirlangan qurilma"
    )
    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.CHOICES,
        verbose_name="Ta'mirlash turi",
        help_text="Ta'mirlash yoki texnik xizmat ko'rsatish turi"
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.CHOICES,
        default=MaintenanceStatus.SCHEDULED,
        verbose_name="Holat",
        help_text="Ta'mirlash jarayonining holati",
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=MaintenancePriority.CHOICES,
        default=MaintenancePriority.MEDIUM,
        verbose_name="Muhimlik darajasi",
        help_text="Ta'mirlashning muhimlik darajasi",
        db_index=True
    )

    # Schedule
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Rejalashtirilgan sana",
        help_text="Ta'mirlash rejalashtirilgan vaqt"
    )
    started_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Boshlangan sana",
        help_text="Ta'mirlash boshlangan vaqt"
    )
    performed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Bajarilgan sana",
        help_text="Ta'mirlash tugallangan vaqt",
        db_index=True
    )
    next_maintenance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Keyingi ta'mirlash sanasi",
        help_text="Keyingi rejali ta'mirlash sanasi"
    )

    # Work Description
    description = models.TextField(
        verbose_name="Tavsif",
        help_text="Ta'mirlash ishlarining tavsifi"
    )
    problem_found = models.TextField(
        blank=True,
        verbose_name="Topilgan muammo",
        help_text="Aniqlangan muammo yoki nosozlik"
    )
    solution_applied = models.TextField(
        blank=True,
        verbose_name="Qo'llangan yechim",
        help_text="Qo'llangan yechim yoki ta'mirlash"
    )
    parts_replaced = models.TextField(
        blank=True,
        verbose_name="Almashtirilgan qismlar",
        help_text="Almashtirilgan ehtiyot qismlar ro'yxati"
    )

    # Personnel
    performed_by = models.CharField(
        max_length=200,
        verbose_name="Bajargan",
        help_text="Ta'mirlashni bajargan shaxs yoki tashkilot"
    )
    technician = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_performed',
        verbose_name="Texnik",
        help_text="Ta'mirlashni bajargan texnik hodim"
    )
    vendor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tashqi tashkilot",
        help_text="Ta'mirlashni bajargan tashqi tashkilot"
    )

    # Costs
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Taxminiy xarajat",
        help_text="Taxminiy umumiy xarajat",
        validators=[validate_positive_price]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Haqiqiy xarajat",
        help_text="Haqiqiy umumiy xarajat",
        validators=[validate_positive_price]
    )
    labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ish haqi",
        help_text="Ish haqi xarajatlari",
        validators=[validate_positive_price]
    )
    parts_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ehtiyot qismlar narxi",
        help_text="Ehtiyot qismlar xarajatlari",
        validators=[validate_positive_price]
    )

    # Additional
    downtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="To'xtash vaqti (soat)",
        help_text="Qurilma ishlamagan vaqt (soatlarda)"
    )
    warranty_claim = models.BooleanField(
        default=False,
        verbose_name="Kafolat bo'yicha",
        help_text="Kafolat bo'yicha ta'mirlash"
    )
    preventive = models.BooleanField(
        default=False,
        verbose_name="Profilaktik",
        help_text="Profilaktik ta'mirlash"
    )
    attachments = models.FileField(
        upload_to=UploadPaths.MAINTENANCE_DOCUMENTS,
        blank=True,
        null=True,
        verbose_name="Qo'shimcha hujjatlar",
        help_text="Texnik hujjatlar, hisobotlar va boshqalar"
    )

    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_created',
        verbose_name="Yaratgan",
        help_text="Yozuvni yaratgan foydalanuvchi"
    )

    class Meta:
        verbose_name = "Ta'mirlash yozuvi"
        verbose_name_plural = "Ta'mirlash yozuvlari"
        ordering = ['-performed_date', '-created_at']
        indexes = [
            models.Index(fields=['equipment', 'performed_date']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['maintenance_type']),
        ]

    def __str__(self) -> str:
        """String representation of maintenance record."""
        return f"{self.equipment.name} - {self.get_maintenance_type_display()} ({self.get_status_display()})"

    def get_total_cost(self) -> float:
        """
        Calculate total maintenance cost.

        Returns sum of labor and parts costs.

        Returns:
            Total cost as float

        Example:
            >>> record.get_total_cost()
            350.00
        """
        return float(self.labor_cost) + float(self.parts_cost)

    def mark_completed(self, user=None, actual_cost=None):
        """
        Mark maintenance as completed.

        Args:
            user: User completing the maintenance
            actual_cost: Actual cost (optional)

        Example:
            >>> record.mark_completed(user=request.user, actual_cost=300.00)
        """
        self.status = MaintenanceStatus.COMPLETED
        self.performed_date = timezone.now()
        if actual_cost is not None:
            self.actual_cost = actual_cost
        if user:
            self.created_by = user
        self.save()


# ============================================
# Audit Log Models
# ============================================

class AuditLog(TimeStampedModel):
    """
    Comprehensive audit trail for all system activities.

    Records all significant actions in the system for security,
    compliance, and debugging purposes.

    Attributes:
        user: User who performed action
        action: Type of action (CREATE, UPDATE, DELETE, etc.)
        timestamp: When action occurred (from TimeStampedModel)

        Target Object:
        content_type: Type of object affected
        object_id: ID of object affected
        content_object: Generic FK to actual object
        model_name: Name of model
        object_repr: String representation of object

        Change Tracking:
        changes: JSON of what changed
        old_values: JSON of old values
        new_values: JSON of new values

        Context:
        description: Human-readable description
        ip_address: IP address of user
        user_agent: Browser user agent

        Status:
        success: Whether action succeeded
        error_message: Error if action failed

    Example:
        AuditLog.log_action(
            user=request.user,
            action=AuditAction.UPDATE,
            obj=equipment,
            description="Updated equipment status",
            ip_address=get_client_ip(request)
        )
    """
    # Core Fields
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Foydalanuvchi",
        help_text="Harakatni amalga oshirgan foydalanuvchi"
    )
    action = models.CharField(
        max_length=20,
        choices=AuditAction.CHOICES,
        verbose_name="Harakat",
        help_text="Amalga oshirilgan harakat turi",
        db_index=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Vaqt",
        help_text="Harakat amalga oshirilgan vaqt"
    )

    # Target Object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Model turi",
        help_text="Ta'sirlangan obyekt turi"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Obyekt ID",
        help_text="Ta'sirlangan obyekt ID raqami"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Model nomi",
        help_text="Model klassi nomi"
    )
    object_repr = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Obyekt tasviri",
        help_text="Obyektning string tasviri"
    )

    # Change Tracking
    changes = models.JSONField(
        blank=True,
        null=True,
        verbose_name="O'zgarishlar",
        help_text="O'zgarishlar JSON formatda"
    )
    old_values = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Eski qiymatlar",
        help_text="O'zgarishdan oldingi qiymatlar"
    )
    new_values = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Yangi qiymatlar",
        help_text="O'zgarishdan keyingi qiymatlar"
    )

    # Context
    description = models.TextField(
        blank=True,
        verbose_name="Tavsif",
        help_text="Harakatning qisqa tavsifi"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP manzil",
        help_text="Foydalanuvchining IP manzili"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="Brauzer user agent string"
    )

    # Status
    success = models.BooleanField(
        default=True,
        verbose_name="Muvaffaqiyatli",
        help_text="Harakat muvaffaqiyatli amalga oshirilganmi",
        db_index=True
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Xatolik xabari",
        help_text="Xatolik yuz berganda xatolik xabari"
    )

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self) -> str:
        """String representation of audit log."""
        user_str = self.user.username if self.user else "Noma'lum"
        return f"{user_str} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log_action(cls, user, action, obj=None, description='', changes=None,
                   old_values=None, new_values=None, ip_address=None,
                   user_agent=None, success=True, error_message=''):
        """
        Create an audit log entry.

        Class method for easy audit logging throughout the application.

        Args:
            user: User performing action
            action: Action type (from AuditAction constants)
            obj: Object being acted upon (optional)
            description: Human-readable description
            changes: Dictionary of changes
            old_values: Dictionary of old values
            new_values: Dictionary of new values
            ip_address: IP address of user
            user_agent: Browser user agent
            success: Whether action succeeded
            error_message: Error message if failed

        Returns:
            Created AuditLog instance

        Example:
            >>> AuditLog.log_action(
            ...     user=request.user,
            ...     action=AuditAction.UPDATE,
            ...     obj=equipment,
            ...     description="Changed status to MAINTENANCE",
            ...     changes={'status': {'old': 'AVAILABLE', 'new': 'MAINTENANCE'}}
            ... )
        """
        log = cls(
            user=user,
            action=action,
            description=description,
            changes=changes,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )

        if obj:
            log.content_object = obj
            log.model_name = obj.__class__.__name__
            log.object_repr = str(obj)[:200]

        log.save()
        return log


# ============================================
# OTP Models
# ============================================

class PasswordChangeOTP(TimeStampedModel):
    """
    One-Time Password for password reset.

    Generates and validates OTP codes for secure password reset.
    OTPs expire after a set time period.

    Attributes:
        user: User requesting password reset
        otp_code: 6-digit numeric OTP code
        created_at: When OTP was created (from TimeStampedModel)
        expires_at: When OTP expires
        is_used: Whether OTP has been used
        used_at: When OTP was used
        ip_address: IP address of requester

    Example:
        otp = PasswordChangeOTP.generate_otp(
            user=user,
            ip_address=get_client_ip(request)
        )
        # Send otp.otp_code via email

        # Later, verify:
        verified_otp = PasswordChangeOTP.verify_otp(user, entered_code)
        if verified_otp:
            # Allow password change
            verified_otp.mark_as_used()
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_change_otps',
        verbose_name="Foydalanuvchi",
        help_text="OTP so'ragan foydalanuvchi"
    )
    otp_code = models.CharField(
        max_length=6,
        verbose_name="OTP kod",
        help_text="6 raqamli bir martalik kod",
        db_index=True
    )
    expires_at = models.DateTimeField(
        verbose_name="Amal qilish muddati",
        help_text="OTP kodning amal qilish muddati",
        db_index=True
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Ishlatilgan",
        help_text="OTP ishlatilganmi",
        db_index=True
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ishlatilgan vaqt",
        help_text="OTP ishlatilgan vaqt"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP manzil",
        help_text="So'rov yuborilgan IP manzil"
    )

    class Meta:
        verbose_name = "Parol o'zgartirish OTP"
        verbose_name_plural = "Parol o'zgartirish OTP kodlari"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['otp_code', 'is_used']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self) -> str:
        """String representation of OTP."""
        return f"{self.user.username} - {self.otp_code} ({'Ishlatilgan' if self.is_used else 'Faol'})"

    def is_valid(self) -> bool:
        """
        Check if OTP is still valid.

        OTP is valid if not used and not expired.

        Returns:
            True if valid, False otherwise

        Example:
            >>> if otp.is_valid():
            ...     # Allow password change
        """
        if self.is_used:
            return False
        return timezone.now() < self.expires_at

    def mark_as_used(self):
        """
        Mark OTP as used.

        Call this after successfully using OTP for password change.

        Example:
            >>> otp.mark_as_used()
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    @classmethod
    def generate_otp(cls, user, ip_address=None):
        """
        Generate new OTP for user.

        Automatically invalidates any existing unused OTPs for the user.

        Args:
            user: User requesting OTP
            ip_address: IP address of requester (optional)

        Returns:
            New OTP instance

        Example:
            >>> otp = PasswordChangeOTP.generate_otp(
            ...     user=user,
            ...     ip_address="192.168.1.1"
            ... )
            >>> send_email(user.email, f"Your code: {otp.otp_code}")
        """
        # Generate secure OTP code
        otp_code = generate_otp_code()

        # Calculate expiry time
        expires_at = get_otp_expiry_time()

        # Invalidate old unused OTPs
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new OTP
        otp = cls.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=expires_at,
            ip_address=ip_address
        )

        return otp

    @classmethod
    def verify_otp(cls, user, otp_code):
        """
        Verify OTP code for user.

        Args:
            user: User attempting verification
            otp_code: OTP code to verify

        Returns:
            OTP instance if valid, None otherwise

        Example:
            >>> otp = PasswordChangeOTP.verify_otp(user, "123456")
            >>> if otp:
            ...     # Code is valid
            ...     otp.mark_as_used()
        """
        try:
            otp = cls.objects.get(
                user=user,
                otp_code=otp_code,
                is_used=False
            )

            if otp.is_valid():
                return otp
            else:
                return None

        except cls.DoesNotExist:
            return None
