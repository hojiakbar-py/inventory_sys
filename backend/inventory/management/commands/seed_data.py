"""
Management command to seed the database with sample data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from inventory.models import (
    Branch, Department, Employee, EquipmentCategory, Equipment,
    Assignment, InventoryCheck, MaintenanceRecord
)


class Command(BaseCommand):
    help = "Bazaga namuna ma'lumotlar kiritish"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help="Mavjud ma'lumotlarni o'chirish",
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Mavjud ma'lumotlar o'chirilmoqda...")
            self.clear_data()

        self.stdout.write("Ma'lumotlar kiritilmoqda...")

        # Create admin user if not exists
        admin_user = self.create_admin_user()

        # Create branches
        branches = self.create_branches()

        # Create departments
        departments = self.create_departments(branches)

        # Create employees
        employees = self.create_employees(branches, departments)

        # Create equipment categories
        categories = self.create_categories()

        # Create equipment
        equipment_list = self.create_equipment(branches, categories, admin_user)

        # Create assignments
        self.create_assignments(equipment_list, employees, admin_user)

        self.stdout.write(self.style.SUCCESS("Ma'lumotlar muvaffaqiyatli kiritildi!"))
        self.print_summary()

    def clear_data(self):
        """Clear existing sample data."""
        Assignment.objects.all().delete()
        InventoryCheck.objects.all().delete()
        MaintenanceRecord.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentCategory.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        Branch.objects.all().delete()
        self.stdout.write(self.style.WARNING("Barcha ma'lumotlar o'chirildi"))

    def create_admin_user(self):
        """Create or get admin user."""
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@inventory.uz',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(f"  Admin user yaratildi: admin / admin123")
        return user

    def create_branches(self):
        """Create sample branches."""
        branches_data = [
            {
                'code': 'HQ-001',
                'name': 'Bosh Ofis',
                'address': 'Amir Temur ko\'chasi 107A',
                'city': 'Toshkent',
                'region': 'Toshkent shahri',
                'branch_type': 'HEADQUARTERS',
                'phone': '+998712345678',
                'email': 'info@company.uz',
            },
            {
                'code': 'SAM-001',
                'name': 'Samarqand Filiali',
                'address': 'Registon ko\'chasi 15',
                'city': 'Samarqand',
                'region': 'Samarqand viloyati',
                'branch_type': 'REGIONAL',
                'phone': '+998662234567',
                'email': 'samarkand@company.uz',
            },
            {
                'code': 'BUX-001',
                'name': 'Buxoro Filiali',
                'address': 'Lyabi-Hauz ko\'chasi 8',
                'city': 'Buxoro',
                'region': 'Buxoro viloyati',
                'branch_type': 'REGIONAL',
                'phone': '+998652345678',
                'email': 'bukhara@company.uz',
            },
            {
                'code': 'FER-001',
                'name': "Farg'ona Filiali",
                'address': 'Mustaqillik ko\'chasi 45',
                'city': "Farg'ona",
                'region': "Farg'ona viloyati",
                'branch_type': 'LOCAL',
                'phone': '+998732345678',
                'email': 'fergana@company.uz',
            },
            {
                'code': 'WH-001',
                'name': 'Markaziy Ombor',
                'address': 'Sanoat ko\'chasi 100',
                'city': 'Toshkent',
                'region': 'Toshkent viloyati',
                'branch_type': 'WAREHOUSE',
                'phone': '+998712345999',
                'email': 'warehouse@company.uz',
                'is_warehouse': True,
            },
        ]

        branches = []
        for data in branches_data:
            branch, created = Branch.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            branches.append(branch)
            status = "yaratildi" if created else "mavjud"
            self.stdout.write(f"  Filial: {branch.name} - {status}")

        # Set parent branches
        if len(branches) > 1:
            for branch in branches[1:]:
                if branch.branch_type != 'HEADQUARTERS':
                    branch.parent_branch = branches[0]
                    branch.save()

        return branches

    def create_departments(self, branches):
        """Create sample departments."""
        departments_data = [
            {'code': 'IT', 'name': 'IT Bo\'limi', 'location': '3-qavat'},
            {'code': 'HR', 'name': 'Kadrlar bo\'limi', 'location': '2-qavat'},
            {'code': 'FIN', 'name': 'Moliya bo\'limi', 'location': '2-qavat'},
            {'code': 'SALES', 'name': 'Sotuv bo\'limi', 'location': '1-qavat'},
            {'code': 'LOG', 'name': 'Logistika bo\'limi', 'location': '1-qavat'},
            {'code': 'ADMIN', 'name': 'Ma\'muriyat', 'location': '4-qavat'},
            {'code': 'TECH', 'name': 'Texnik xizmat', 'location': 'Basement'},
            {'code': 'SEC', 'name': 'Xavfsizlik bo\'limi', 'location': '1-qavat'},
        ]

        departments = []
        main_branch = branches[0] if branches else None

        for data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=data['code'],
                branch=main_branch,
                defaults={
                    'name': data['name'],
                    'location': data['location'],
                }
            )
            departments.append(dept)
            status = "yaratildi" if created else "mavjud"
            self.stdout.write(f"  Bo'lim: {dept.name} - {status}")

        return departments

    def create_employees(self, branches, departments):
        """Create sample employees."""
        employees_data = [
            {'employee_id': 'EMP001', 'first_name': 'Aziz', 'last_name': 'Karimov', 'position': 'IT Menejer', 'dept': 'IT'},
            {'employee_id': 'EMP002', 'first_name': 'Dilnoza', 'last_name': 'Rahimova', 'position': 'HR Mutaxassisi', 'dept': 'HR'},
            {'employee_id': 'EMP003', 'first_name': 'Bobur', 'last_name': 'Aliyev', 'position': 'Dasturchi', 'dept': 'IT'},
            {'employee_id': 'EMP004', 'first_name': 'Gulnora', 'last_name': 'Saidova', 'position': 'Buxgalter', 'dept': 'FIN'},
            {'employee_id': 'EMP005', 'first_name': 'Jasur', 'last_name': 'Toshmatov', 'position': 'Sotuv menejeri', 'dept': 'SALES'},
            {'employee_id': 'EMP006', 'first_name': 'Nodira', 'last_name': 'Yusupova', 'position': 'Logist', 'dept': 'LOG'},
            {'employee_id': 'EMP007', 'first_name': 'Rustam', 'last_name': 'Qodirov', 'position': 'Tizim administratori', 'dept': 'IT'},
            {'employee_id': 'EMP008', 'first_name': 'Shahlo', 'last_name': 'Mirzoeva', 'position': 'Moliya menejeri', 'dept': 'FIN'},
            {'employee_id': 'EMP009', 'first_name': 'Kamol', 'last_name': 'Xolmatov', 'position': 'Texnik mutaxassis', 'dept': 'TECH'},
            {'employee_id': 'EMP010', 'first_name': 'Zarina', 'last_name': 'Nazarova', 'position': 'Ma\'mur', 'dept': 'ADMIN'},
            {'employee_id': 'EMP011', 'first_name': 'Otabek', 'last_name': 'Sodiqov', 'position': 'Xavfsizlik xodimi', 'dept': 'SEC'},
            {'employee_id': 'EMP012', 'first_name': 'Malika', 'last_name': 'Ergasheva', 'position': 'Katta dasturchi', 'dept': 'IT'},
            {'employee_id': 'EMP013', 'first_name': 'Sardor', 'last_name': 'Umarov', 'position': 'DevOps muhandisi', 'dept': 'IT'},
            {'employee_id': 'EMP014', 'first_name': 'Feruza', 'last_name': 'Abdullayeva', 'position': 'HR Menejeri', 'dept': 'HR'},
            {'employee_id': 'EMP015', 'first_name': 'Jamshid', 'last_name': 'Tursunov', 'position': 'Sotuv agenti', 'dept': 'SALES'},
        ]

        employees = []
        dept_map = {d.code: d for d in departments}
        main_branch = branches[0] if branches else None

        for data in employees_data:
            dept = dept_map.get(data['dept'])
            emp, created = Employee.objects.get_or_create(
                employee_id=data['employee_id'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'position': data['position'],
                    'department': dept,
                    'branch': main_branch,
                    'email': f"{data['first_name'].lower()}.{data['last_name'].lower()}@company.uz",
                    'phone': f"+99890{random.randint(1000000, 9999999)}",
                    'hire_date': date.today() - timedelta(days=random.randint(30, 1000)),
                }
            )
            employees.append(emp)
            status = "yaratildi" if created else "mavjud"
            self.stdout.write(f"  Xodim: {emp.get_full_name()} - {status}")

        return employees

    def create_categories(self):
        """Create equipment categories."""
        categories_data = [
            {'code': 'COMP', 'name': 'Kompyuterlar', 'description': 'Desktop va noutbuklar'},
            {'code': 'MON', 'name': 'Monitorlar', 'description': 'Kompyuter monitorlari'},
            {'code': 'PRINT', 'name': 'Printerlar', 'description': 'Printer va skanerlar'},
            {'code': 'NET', 'name': 'Tarmoq jihozlari', 'description': 'Router, switch va boshqalar'},
            {'code': 'FURN', 'name': 'Mebel', 'description': 'Ofis mebellari'},
            {'code': 'PHONE', 'name': 'Telefonlar', 'description': 'Mobil va statsionar telefonlar'},
            {'code': 'SERVER', 'name': 'Serverlar', 'description': 'Server jihozlari'},
            {'code': 'OTHER', 'name': 'Boshqa jihozlar', 'description': 'Boshqa ofis jihozlari'},
        ]

        categories = []
        for data in categories_data:
            # First try to find by code or name
            cat = EquipmentCategory.objects.filter(code=data['code']).first()
            if not cat:
                cat = EquipmentCategory.objects.filter(name=data['name']).first()

            if cat:
                # Update existing
                cat.code = data['code']
                cat.name = data['name']
                cat.description = data['description']
                cat.save()
                created = False
            else:
                # Create new
                cat = EquipmentCategory.objects.create(
                    code=data['code'],
                    name=data['name'],
                    description=data['description'],
                )
                created = True

            categories.append(cat)
            status = "yaratildi" if created else "mavjud"
            self.stdout.write(f"  Kategoriya: {cat.name} - {status}")

        return categories

    def create_equipment(self, branches, categories, user):
        """Create sample equipment."""
        equipment_data = [
            # Kompyuterlar
            {'inv': 'INV-2024-001', 'name': 'Dell OptiPlex 7090', 'cat': 'COMP', 'manufacturer': 'Dell', 'model': 'OptiPlex 7090', 'price': 12000000},
            {'inv': 'INV-2024-002', 'name': 'HP ProDesk 400', 'cat': 'COMP', 'manufacturer': 'HP', 'model': 'ProDesk 400 G7', 'price': 10500000},
            {'inv': 'INV-2024-003', 'name': 'Lenovo ThinkCentre', 'cat': 'COMP', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M70q', 'price': 11000000},
            {'inv': 'INV-2024-004', 'name': 'Dell Latitude 5520', 'cat': 'COMP', 'manufacturer': 'Dell', 'model': 'Latitude 5520', 'price': 15000000},
            {'inv': 'INV-2024-005', 'name': 'HP EliteBook 840', 'cat': 'COMP', 'manufacturer': 'HP', 'model': 'EliteBook 840 G8', 'price': 18000000},
            {'inv': 'INV-2024-006', 'name': 'Lenovo ThinkPad T14', 'cat': 'COMP', 'manufacturer': 'Lenovo', 'model': 'ThinkPad T14', 'price': 16500000},

            # Monitorlar
            {'inv': 'INV-2024-007', 'name': 'Dell P2422H Monitor', 'cat': 'MON', 'manufacturer': 'Dell', 'model': 'P2422H', 'price': 3500000},
            {'inv': 'INV-2024-008', 'name': 'Samsung 27" Monitor', 'cat': 'MON', 'manufacturer': 'Samsung', 'model': 'S27R650', 'price': 4000000},
            {'inv': 'INV-2024-009', 'name': 'LG 24" IPS Monitor', 'cat': 'MON', 'manufacturer': 'LG', 'model': '24MK430H', 'price': 2800000},
            {'inv': 'INV-2024-010', 'name': 'HP E24 G4 Monitor', 'cat': 'MON', 'manufacturer': 'HP', 'model': 'E24 G4', 'price': 3200000},

            # Printerlar
            {'inv': 'INV-2024-011', 'name': 'HP LaserJet Pro', 'cat': 'PRINT', 'manufacturer': 'HP', 'model': 'LaserJet Pro M404n', 'price': 5500000},
            {'inv': 'INV-2024-012', 'name': 'Canon imageCLASS', 'cat': 'PRINT', 'manufacturer': 'Canon', 'model': 'imageCLASS MF445dw', 'price': 7000000},
            {'inv': 'INV-2024-013', 'name': 'Epson EcoTank', 'cat': 'PRINT', 'manufacturer': 'Epson', 'model': 'EcoTank L3250', 'price': 3500000},

            # Tarmoq jihozlari
            {'inv': 'INV-2024-014', 'name': 'Cisco Switch 24 port', 'cat': 'NET', 'manufacturer': 'Cisco', 'model': 'SG350-28', 'price': 8000000},
            {'inv': 'INV-2024-015', 'name': 'MikroTik Router', 'cat': 'NET', 'manufacturer': 'MikroTik', 'model': 'RB4011iGS+', 'price': 6500000},
            {'inv': 'INV-2024-016', 'name': 'TP-Link WiFi AP', 'cat': 'NET', 'manufacturer': 'TP-Link', 'model': 'EAP245', 'price': 1500000},

            # Serverlar
            {'inv': 'INV-2024-017', 'name': 'Dell PowerEdge R740', 'cat': 'SERVER', 'manufacturer': 'Dell', 'model': 'PowerEdge R740', 'price': 85000000},
            {'inv': 'INV-2024-018', 'name': 'HP ProLiant DL380', 'cat': 'SERVER', 'manufacturer': 'HP', 'model': 'ProLiant DL380 Gen10', 'price': 75000000},

            # Telefonlar
            {'inv': 'INV-2024-019', 'name': 'iPhone 14 Pro', 'cat': 'PHONE', 'manufacturer': 'Apple', 'model': 'iPhone 14 Pro', 'price': 15000000},
            {'inv': 'INV-2024-020', 'name': 'Samsung Galaxy S23', 'cat': 'PHONE', 'manufacturer': 'Samsung', 'model': 'Galaxy S23', 'price': 12000000},
            {'inv': 'INV-2024-021', 'name': 'Cisco IP Phone', 'cat': 'PHONE', 'manufacturer': 'Cisco', 'model': 'IP Phone 8845', 'price': 4500000},

            # Mebel
            {'inv': 'INV-2024-022', 'name': 'Ofis stoli', 'cat': 'FURN', 'manufacturer': 'Local', 'model': 'Executive Desk', 'price': 3500000},
            {'inv': 'INV-2024-023', 'name': 'Ergonomik kreslo', 'cat': 'FURN', 'manufacturer': 'Herman Miller', 'model': 'Aeron', 'price': 8000000},
            {'inv': 'INV-2024-024', 'name': 'Shkaf', 'cat': 'FURN', 'manufacturer': 'Local', 'model': 'Office Cabinet', 'price': 2500000},

            # Boshqa
            {'inv': 'INV-2024-025', 'name': 'Proyektor', 'cat': 'OTHER', 'manufacturer': 'Epson', 'model': 'EB-X51', 'price': 7500000},
            {'inv': 'INV-2024-026', 'name': 'UPS 1500VA', 'cat': 'OTHER', 'manufacturer': 'APC', 'model': 'Back-UPS 1500', 'price': 2500000},
            {'inv': 'INV-2024-027', 'name': 'Konditsioner', 'cat': 'OTHER', 'manufacturer': 'Samsung', 'model': 'AR12TQHQAURNER', 'price': 6000000},
        ]

        equipment_list = []
        cat_map = {c.code: c for c in categories}
        main_branch = branches[0] if branches else None
        statuses = ['AVAILABLE', 'AVAILABLE', 'AVAILABLE', 'ASSIGNED', 'MAINTENANCE']
        conditions = ['NEW', 'EXCELLENT', 'GOOD', 'GOOD', 'FAIR']

        for data in equipment_data:
            cat = cat_map.get(data['cat'])
            serial = f"SN-{random.randint(100000, 999999)}"
            purchase_date = date.today() - timedelta(days=random.randint(30, 365))
            warranty_expiry = purchase_date + timedelta(days=365 * 2)  # 2 year warranty

            equip, created = Equipment.objects.get_or_create(
                inventory_number=data['inv'],
                defaults={
                    'name': data['name'],
                    'serial_number': serial,
                    'category': cat,
                    'branch': main_branch,
                    'manufacturer': data['manufacturer'],
                    'model': data['model'],
                    'purchase_price': Decimal(data['price']),
                    'purchase_date': purchase_date,
                    'warranty_expiry': warranty_expiry,
                    'status': random.choice(statuses),
                    'condition': random.choice(conditions),
                    'created_by': user,
                }
            )
            equipment_list.append(equip)
            status = "yaratildi" if created else "mavjud"
            self.stdout.write(f"  Qurilma: {equip.name} ({equip.inventory_number}) - {status}")

        return equipment_list

    def create_assignments(self, equipment_list, employees, user):
        """Create sample assignments."""
        # Get available equipment
        available_equipment = [e for e in equipment_list if e.status == 'AVAILABLE'][:10]

        for i, equip in enumerate(available_equipment):
            if i >= len(employees):
                break

            emp = employees[i]
            assignment, created = Assignment.objects.get_or_create(
                equipment=equip,
                employee=emp,
                return_date__isnull=True,
                defaults={
                    'assigned_date': date.today() - timedelta(days=random.randint(1, 60)),
                    'purpose': 'Ish uchun',
                    'condition_on_assignment': equip.condition,
                    'assigned_by': user,
                }
            )

            if created:
                equip.status = 'ASSIGNED'
                equip.save()
                self.stdout.write(f"  Tayinlash: {equip.name} -> {emp.get_full_name()}")

    def print_summary(self):
        """Print summary of created data."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("YAKUNIY HISOBOT:"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"  Filiallar: {Branch.objects.count()}")
        self.stdout.write(f"  Bo'limlar: {Department.objects.count()}")
        self.stdout.write(f"  Xodimlar: {Employee.objects.count()}")
        self.stdout.write(f"  Kategoriyalar: {EquipmentCategory.objects.count()}")
        self.stdout.write(f"  Qurilmalar: {Equipment.objects.count()}")
        self.stdout.write(f"  Tayinlashlar: {Assignment.objects.count()}")
        self.stdout.write("=" * 50)
