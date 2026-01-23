"""
Constants for Inventory Management System.

This module contains all constant values used throughout the application.
Using constants improves maintainability and reduces magic strings/numbers.
"""

# ============================================
# Equipment Constants
# ============================================

class EquipmentStatus:
    """Equipment status choices."""
    AVAILABLE = 'AVAILABLE'
    ASSIGNED = 'ASSIGNED'
    MAINTENANCE = 'MAINTENANCE'
    RETIRED = 'RETIRED'
    DAMAGED = 'DAMAGED'
    LOST = 'LOST'

    CHOICES = (
        (AVAILABLE, 'Mavjud'),
        (ASSIGNED, 'Tayinlangan'),
        (MAINTENANCE, 'Ta\'mirlash'),
        (RETIRED, 'Foydalanishdan chiqarilgan'),
        (DAMAGED, 'Buzilgan'),
        (LOST, 'Yo\'qolgan'),
    )


class EquipmentCondition:
    """Equipment physical condition choices."""
    NEW = 'NEW'
    EXCELLENT = 'EXCELLENT'
    GOOD = 'GOOD'
    FAIR = 'FAIR'
    POOR = 'POOR'

    CHOICES = (
        (NEW, 'Yangi'),
        (EXCELLENT, 'A\'lo'),
        (GOOD, 'Yaxshi'),
        (FAIR, 'O\'rtacha'),
        (POOR, 'Yomon'),
    )


# ============================================
# Maintenance Constants
# ============================================

class MaintenanceType:
    """Maintenance record type choices."""
    REPAIR = 'REPAIR'
    UPGRADE = 'UPGRADE'
    CLEANING = 'CLEANING'
    INSPECTION = 'INSPECTION'
    CALIBRATION = 'CALIBRATION'
    SOFTWARE_UPDATE = 'SOFTWARE_UPDATE'

    CHOICES = (
        (REPAIR, 'Ta\'mirlash'),
        (UPGRADE, 'Yangilash'),
        (CLEANING, 'Tozalash'),
        (INSPECTION, 'Tekshiruv'),
        (CALIBRATION, 'Kalibrlash'),
        (SOFTWARE_UPDATE, 'Dasturiy ta\'minot yangilash'),
    )


class MaintenanceStatus:
    """Maintenance record status choices."""
    SCHEDULED = 'SCHEDULED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

    CHOICES = (
        (SCHEDULED, 'Rejalashtirilgan'),
        (IN_PROGRESS, 'Jarayonda'),
        (COMPLETED, 'Bajarilgan'),
        (CANCELLED, 'Bekor qilingan'),
    )


class MaintenancePriority:
    """Maintenance record priority choices."""
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

    CHOICES = (
        (LOW, 'Past'),
        (MEDIUM, 'O\'rta'),
        (HIGH, 'Yuqori'),
        (CRITICAL, 'Kritik'),
    )


# ============================================
# Inventory Check Constants
# ============================================

class CheckType:
    """Inventory check type choices."""
    SCHEDULED = 'SCHEDULED'
    RANDOM = 'RANDOM'
    INCIDENT = 'INCIDENT'
    ANNUAL = 'ANNUAL'

    CHOICES = (
        (SCHEDULED, 'Rejalashtirilgan'),
        (RANDOM, 'Tasodifiy'),
        (INCIDENT, 'Hodisa bo\'yicha'),
        (ANNUAL, 'Yillik'),
    )


# ============================================
# Audit Log Constants
# ============================================

class AuditAction:
    """Audit log action choices."""
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    ASSIGN = 'ASSIGN'
    RETURN = 'RETURN'
    CHECK = 'CHECK'
    MAINTAIN = 'MAINTAIN'
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    EXPORT = 'EXPORT'
    IMPORT = 'IMPORT'

    CHOICES = (
        (CREATE, 'Yaratildi'),
        (UPDATE, 'O\'zgartirildi'),
        (DELETE, 'O\'chirildi'),
        (ASSIGN, 'Tayinlandi'),
        (RETURN, 'Qaytarildi'),
        (CHECK, 'Tekshirildi'),
        (MAINTAIN, 'Ta\'mirlandi'),
        (APPROVE, 'Tasdiqlandi'),
        (REJECT, 'Rad etildi'),
        (LOGIN, 'Kirish'),
        (LOGOUT, 'Chiqish'),
        (EXPORT, 'Eksport'),
        (IMPORT, 'Import'),
    )


# ============================================
# Validation Constants
# ============================================

class ValidationConstants:
    """Validation-related constants."""
    MIN_INVENTORY_NUMBER_LENGTH = 3
    MIN_EMPLOYEE_ID_LENGTH = 3
    MIN_SERIAL_NUMBER_LENGTH = 3
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 8

    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
    ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx']

    # Uzbekistan phone pattern: +998XXXXXXXXX
    PHONE_PATTERN = r'^\+?998[0-9]{9}$'

    # Passport series pattern: XX1234567 (2 letters + 7 digits)
    PASSPORT_PATTERN = r'^[A-Z]{2}[0-9]{7}$'

    # Email validation is handled by Django's EmailField


# ============================================
# Business Logic Constants
# ============================================

class BusinessConstants:
    """Business logic related constants."""
    OTP_EXPIRY_MINUTES = 10
    OTP_CODE_LENGTH = 6

    DEFAULT_DEPRECIATION_RATE = 0.0
    MIN_DEPRECIATION_RATE = 0.0
    MAX_DEPRECIATION_RATE = 100.0

    DEFAULT_WARRANTY_MONTHS = 12

    # QR Code settings
    QR_CODE_VERSION = 1
    QR_CODE_BOX_SIZE = 10
    QR_CODE_BORDER = 5

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Export limits
    MAX_EXPORT_RECORDS = 10000


# ============================================
# URL Patterns
# ============================================

class URLPatterns:
    """URL pattern constants for QR codes and redirects."""
    EQUIPMENT_QR_PATTERN = "/equipment/{inventory_number}"
    EMPLOYEE_QR_PATTERN = "/employee/{employee_id}"


# ============================================
# File Upload Paths
# ============================================

class UploadPaths:
    """File upload directory paths."""
    QR_CODE_EQUIPMENT = 'qr_codes/equipment/'
    QR_CODE_EMPLOYEE = 'qr_codes/employees/'
    EQUIPMENT_IMAGES = 'equipment/'
    SIGNATURES = 'signatures/'
    INVENTORY_CHECK_PHOTOS = 'inventory_checks/'
    MAINTENANCE_DOCUMENTS = 'maintenance_docs/'


# ============================================
# Error Messages
# ============================================

class ErrorMessages:
    """Common error messages for consistency."""
    # Validation errors
    INVALID_INVENTORY_NUMBER = 'Inventar raqam kamida 3 ta belgidan iborat bo\'lishi kerak'
    INVALID_EMPLOYEE_ID = 'Hodim ID kamida 3 ta belgidan iborat bo\'lishi kerak'
    INVALID_PHONE_NUMBER = 'Telefon raqami +998XXXXXXXXX formatida bo\'lishi kerak'
    INVALID_PASSPORT_SERIES = 'Pasport seriyasi XX0000000 formatida bo\'lishi kerak'
    INVALID_SERIAL_NUMBER = 'Seriya raqami kamida 3 ta belgidan iborat bo\'lishi kerak'
    INVALID_PRICE = 'Narx musbat bo\'lishi kerak'
    INVALID_DEPRECIATION_RATE = 'Amortizatsiya foizi 0-100 oralig\'ida bo\'lishi kerak'
    INVALID_FILE_SIZE = f'Fayl hajmi {ValidationConstants.MAX_FILE_SIZE_MB}MB dan oshmasligi kerak'
    INVALID_IMAGE_EXTENSION = 'Faqat JPG, JPEG, PNG formatdagi rasmlar qabul qilinadi'

    # Business logic errors
    EQUIPMENT_NOT_AVAILABLE = 'Bu qurilmani tayinlash mumkin emas. Status: {status}'
    EQUIPMENT_ALREADY_ASSIGNED = 'Qurilma allaqachon tayinlangan. Avval qaytarib oling.'
    EQUIPMENT_NOT_ASSIGNED = 'Qurilma hech kimga tayinlanmagan'

    # Auth errors
    INVALID_CREDENTIALS = 'Foydalanuvchi nomi yoki parol noto\'g\'ri'
    USER_NOT_ACTIVE = 'Foydalanuvchi faol emas'
    INVALID_OTP = 'Noto\'g\'ri yoki muddati o\'tgan OTP kod'

    # Generic errors
    NOT_FOUND = '{model} topilmadi'
    PERMISSION_DENIED = 'Sizda bu amalni bajarish uchun ruxsat yo\'q'
    UNKNOWN_ERROR = 'Noma\'lum xatolik yuz berdi'


# ============================================
# Success Messages
# ============================================

class SuccessMessages:
    """Common success messages for consistency."""
    CREATED = '{model} muvaffaqiyatli yaratildi'
    UPDATED = '{model} muvaffaqiyatli yangilandi'
    DELETED = '{model} muvaffaqiyatli o\'chirildi'

    EQUIPMENT_ASSIGNED = 'Qurilma muvaffaqiyatli tayinlandi'
    EQUIPMENT_RETURNED = 'Qurilma muvaffaqiyatli qaytarildi'

    PASSWORD_CHANGED = 'Parol muvaffaqiyatli o\'zgartirildi'
    PROFILE_UPDATED = 'Profil muvaffaqiyatli yangilandi'

    OTP_SENT = 'OTP kod emailingizga yuborildi. Iltimos, tekshiring.'

    IMPORT_SUCCESS = '{created} ta yaratildi, {updated} ta yangilandi'
    EXPORT_SUCCESS = 'Ma\'lumotlar muvaffaqiyatli eksport qilindi'
