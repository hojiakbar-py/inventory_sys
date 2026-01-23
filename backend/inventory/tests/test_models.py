"""
Model tests for Inventory Management System.

Tests model creation, methods, and relationships.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from inventory.models import (
    Branch, Department, Employee, EquipmentCategory,
    Equipment, Assignment, InventoryCheck, MaintenanceRecord,
    AuditLog, PasswordChangeOTP
)
from inventory.constants import (
    EquipmentStatus, EquipmentCondition, MaintenanceType,
    MaintenanceStatus, MaintenancePriority, AuditAction
)


class BranchModelTest(TestCase):
    """Tests for Branch model."""

    def setUp(self):
        """Set up test data."""
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Amir Temur 107A",
            city="Tashkent",
            region="Tashkent",
            country="Uzbekistan",
            branch_type=Branch.HEADQUARTERS
        )

    def test_branch_creation(self):
        """Test branch is created correctly."""
        self.assertEqual(self.branch.code, "TSK-001")
        self.assertEqual(self.branch.name, "Tashkent Office")
        self.assertEqual(self.branch.city, "Tashkent")
        self.assertTrue(self.branch.is_active)

    def test_branch_str(self):
        """Test branch string representation."""
        self.assertEqual(str(self.branch), "Tashkent Office (Tashkent)")

    def test_get_full_address(self):
        """Test get_full_address method."""
        expected = "Amir Temur 107A, Tashkent, Tashkent, Uzbekistan"
        self.assertEqual(self.branch.get_full_address(), expected)

    def test_is_operational(self):
        """Test is_operational method."""
        self.assertTrue(self.branch.is_operational())

        # Deactivate branch
        self.branch.is_active = False
        self.branch.save()
        self.assertFalse(self.branch.is_operational())

    def test_branch_hierarchy(self):
        """Test parent-child branch relationship."""
        sub_branch = Branch.objects.create(
            code="TSK-002",
            name="Tashkent Sub-Office",
            address="Navoi 1",
            city="Tashkent",
            parent_branch=self.branch,
            branch_type=Branch.LOCAL
        )
        self.assertEqual(sub_branch.parent_branch, self.branch)
        self.assertIn(sub_branch, self.branch.sub_branches.all())


class DepartmentModelTest(TestCase):
    """Tests for Department model."""

    def setUp(self):
        """Set up test data."""
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="Information Technology",
            branch=self.branch,
            location="Building A, Floor 3"
        )

    def test_department_creation(self):
        """Test department is created correctly."""
        self.assertEqual(self.department.code, "IT")
        self.assertEqual(self.department.name, "Information Technology")
        self.assertEqual(self.department.branch, self.branch)

    def test_department_str(self):
        """Test department string representation."""
        self.assertEqual(str(self.department), "Information Technology")


class EmployeeModelTest(TestCase):
    """Tests for Employee model."""

    def setUp(self):
        """Set up test data."""
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="Information Technology",
            branch=self.branch
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            middle_name="Michael",
            branch=self.branch,
            department=self.department,
            position="Software Engineer",
            email="john.doe@test.com"
        )

    def test_employee_creation(self):
        """Test employee is created correctly."""
        self.assertEqual(self.employee.employee_id, "EMP001")
        self.assertEqual(self.employee.first_name, "John")
        self.assertEqual(self.employee.last_name, "Doe")
        self.assertTrue(self.employee.is_active)

    def test_employee_str(self):
        """Test employee string representation."""
        self.assertEqual(str(self.employee), "Doe John (Software Engineer)")

    def test_get_full_name(self):
        """Test get_full_name method."""
        self.assertEqual(self.employee.get_full_name(), "John Michael Doe")

        # Without middle name
        self.employee.middle_name = ""
        self.assertEqual(self.employee.get_full_name(), "John Doe")

    def test_employee_qr_code_generated(self):
        """Test QR code is generated on save."""
        # QR code should be generated
        self.assertIsNotNone(self.employee.qr_code)


class EquipmentCategoryModelTest(TestCase):
    """Tests for EquipmentCategory model."""

    def setUp(self):
        """Set up test data."""
        self.parent_category = EquipmentCategory.objects.create(
            code="COMP",
            name="Computers"
        )
        self.child_category = EquipmentCategory.objects.create(
            code="LAPTOP",
            name="Laptops",
            parent=self.parent_category
        )

    def test_category_creation(self):
        """Test category is created correctly."""
        self.assertEqual(self.parent_category.code, "COMP")
        self.assertEqual(self.parent_category.name, "Computers")

    def test_category_hierarchy(self):
        """Test parent-child category relationship."""
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertIn(self.child_category, self.parent_category.subcategories.all())

    def test_get_all_subcategories(self):
        """Test get_all_subcategories method."""
        grandchild = EquipmentCategory.objects.create(
            code="GAMING",
            name="Gaming Laptops",
            parent=self.child_category
        )
        subcategories = self.parent_category.get_all_subcategories()
        self.assertIn(self.child_category, subcategories)
        self.assertIn(grandchild, subcategories)


class EquipmentModelTest(TestCase):
    """Tests for Equipment model."""

    def setUp(self):
        """Set up test data."""
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.category = EquipmentCategory.objects.create(
            code="LAPTOP",
            name="Laptops"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch,
            category=self.category,
            serial_number="ABC123456",
            purchase_price=Decimal("1500.00"),
            purchase_date=date.today() - timedelta(days=365),
            depreciation_rate=Decimal("20.00"),
            warranty_expiry=date.today() + timedelta(days=365),
            status=EquipmentStatus.AVAILABLE
        )

    def test_equipment_creation(self):
        """Test equipment is created correctly."""
        self.assertEqual(self.equipment.inventory_number, "INV-001")
        self.assertEqual(self.equipment.name, "Dell XPS 15")
        self.assertEqual(self.equipment.status, EquipmentStatus.AVAILABLE)

    def test_equipment_str(self):
        """Test equipment string representation."""
        self.assertEqual(str(self.equipment), "Dell XPS 15 (INV-001)")

    def test_is_warranty_active(self):
        """Test is_warranty_active method."""
        self.assertTrue(self.equipment.is_warranty_active())

        # Expire warranty
        self.equipment.warranty_expiry = date.today() - timedelta(days=1)
        self.assertFalse(self.equipment.is_warranty_active())

    def test_is_available_for_assignment(self):
        """Test is_available_for_assignment method."""
        self.assertTrue(self.equipment.is_available_for_assignment())

        # Change status
        self.equipment.status = EquipmentStatus.RETIRED
        self.equipment.save()
        self.assertFalse(self.equipment.is_available_for_assignment())

    def test_calculate_current_value(self):
        """Test depreciation calculation."""
        value = self.equipment.calculate_current_value()
        # After 1 year with 20% depreciation, value should be 1200
        self.assertEqual(value, 1200.0)

    def test_equipment_qr_code_generated(self):
        """Test QR code is generated on save."""
        self.assertIsNotNone(self.equipment.qr_code)


class AssignmentModelTest(TestCase):
    """Tests for Assignment model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="IT",
            branch=self.branch
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            branch=self.branch,
            department=self.department,
            position="Engineer"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch,
            status=EquipmentStatus.AVAILABLE
        )
        self.assignment = Assignment.objects.create(
            equipment=self.equipment,
            employee=self.employee,
            assigned_by=self.user,
            condition_on_assignment="Good condition",
            purpose="Work from home"
        )

    def test_assignment_creation(self):
        """Test assignment is created correctly."""
        self.assertEqual(self.assignment.equipment, self.equipment)
        self.assertEqual(self.assignment.employee, self.employee)
        self.assertIsNone(self.assignment.return_date)

    def test_assignment_str(self):
        """Test assignment string representation."""
        expected = "Dell XPS 15 -> John Doe"
        self.assertEqual(str(self.assignment), expected)

    def test_is_active(self):
        """Test is_active method."""
        self.assertTrue(self.assignment.is_active())

    def test_equipment_status_updated(self):
        """Test equipment status is updated on assignment."""
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, EquipmentStatus.ASSIGNED)

    def test_mark_returned(self):
        """Test mark_returned method."""
        self.assignment.mark_returned(
            user=self.user,
            condition="Good condition",
            notes="All accessories included"
        )
        self.assertIsNotNone(self.assignment.return_date)
        self.assertFalse(self.assignment.is_active())

        # Check equipment status
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, EquipmentStatus.AVAILABLE)

    def test_is_overdue(self):
        """Test is_overdue method."""
        self.assignment.expected_return_date = date.today() - timedelta(days=1)
        self.assignment.save()
        self.assertTrue(self.assignment.is_overdue())


class InventoryCheckModelTest(TestCase):
    """Tests for InventoryCheck model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch
        )
        self.check = InventoryCheck.objects.create(
            equipment=self.equipment,
            checked_by=self.user,
            location="Office 201",
            condition="Good working order",
            is_functional=True
        )

    def test_inventory_check_creation(self):
        """Test inventory check is created correctly."""
        self.assertEqual(self.check.equipment, self.equipment)
        self.assertEqual(self.check.location, "Office 201")
        self.assertTrue(self.check.is_functional)

    def test_inventory_check_str(self):
        """Test inventory check string representation."""
        self.assertIn("Dell XPS 15", str(self.check))


class MaintenanceRecordModelTest(TestCase):
    """Tests for MaintenanceRecord model."""

    def setUp(self):
        """Set up test data."""
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch
        )
        self.maintenance = MaintenanceRecord.objects.create(
            equipment=self.equipment,
            maintenance_type=MaintenanceType.REPAIR,
            status=MaintenanceStatus.SCHEDULED,
            priority=MaintenancePriority.HIGH,
            description="Replace keyboard",
            performed_by="IT Support",
            estimated_cost=Decimal("100.00"),
            labor_cost=Decimal("50.00"),
            parts_cost=Decimal("50.00")
        )

    def test_maintenance_creation(self):
        """Test maintenance record is created correctly."""
        self.assertEqual(self.maintenance.equipment, self.equipment)
        self.assertEqual(self.maintenance.maintenance_type, MaintenanceType.REPAIR)
        self.assertEqual(self.maintenance.status, MaintenanceStatus.SCHEDULED)

    def test_get_total_cost(self):
        """Test get_total_cost method."""
        self.assertEqual(self.maintenance.get_total_cost(), 100.0)

    def test_mark_completed(self):
        """Test mark_completed method."""
        self.maintenance.mark_completed(actual_cost=Decimal("90.00"))
        self.assertEqual(self.maintenance.status, MaintenanceStatus.COMPLETED)
        self.assertIsNotNone(self.maintenance.performed_date)
        self.assertEqual(self.maintenance.actual_cost, Decimal("90.00"))


class AuditLogModelTest(TestCase):
    """Tests for AuditLog model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )

    def test_log_action(self):
        """Test log_action class method."""
        log = AuditLog.log_action(
            user=self.user,
            action=AuditAction.CREATE,
            obj=self.branch,
            description="Created branch",
            ip_address="127.0.0.1"
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, AuditAction.CREATE)
        self.assertEqual(log.model_name, "Branch")
        self.assertTrue(log.success)


class PasswordChangeOTPModelTest(TestCase):
    """Tests for PasswordChangeOTP model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_generate_otp(self):
        """Test OTP generation."""
        otp = PasswordChangeOTP.generate_otp(
            user=self.user,
            ip_address="127.0.0.1"
        )
        self.assertEqual(otp.user, self.user)
        self.assertEqual(len(otp.otp_code), 6)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertFalse(otp.is_used)

    def test_verify_otp(self):
        """Test OTP verification."""
        otp = PasswordChangeOTP.generate_otp(user=self.user)

        # Verify with correct code
        verified = PasswordChangeOTP.verify_otp(self.user, otp.otp_code)
        self.assertIsNotNone(verified)

        # Verify with wrong code
        wrong = PasswordChangeOTP.verify_otp(self.user, "000000")
        self.assertIsNone(wrong)

    def test_otp_is_valid(self):
        """Test is_valid method."""
        otp = PasswordChangeOTP.generate_otp(user=self.user)
        self.assertTrue(otp.is_valid())

        # Mark as used
        otp.mark_as_used()
        self.assertFalse(otp.is_valid())

    def test_old_otps_invalidated(self):
        """Test that old OTPs are invalidated when new one is generated."""
        otp1 = PasswordChangeOTP.generate_otp(user=self.user)
        otp2 = PasswordChangeOTP.generate_otp(user=self.user)

        otp1.refresh_from_db()
        self.assertTrue(otp1.is_used)
        self.assertFalse(otp2.is_used)
