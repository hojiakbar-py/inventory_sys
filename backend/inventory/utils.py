"""
Utility functions for Inventory Management System.

This module contains reusable utility functions used throughout the application.
Functions are organized by category for easy maintenance and discovery.
"""

import secrets
from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Optional, Dict, Any

import qrcode
from django.core.files import File
from django.conf import settings
from PIL import Image

from .constants import BusinessConstants, UploadPaths


# ============================================
# QR Code Utilities
# ============================================

def generate_qr_code(data: str, filename: str) -> File:
    """
    Generate QR code image from data string.

    Args:
        data: Data to encode in QR code
        filename: Name for the generated file

    Returns:
        Django File object containing QR code image

    Examples:
        >>> qr_file = generate_qr_code("https://example.com/equipment/INV001", "equipment_INV001.png")
        >>> equipment.qr_code.save("qr.png", qr_file, save=False)
    """
    qr = qrcode.QRCode(
        version=BusinessConstants.QR_CODE_VERSION,
        box_size=BusinessConstants.QR_CODE_BOX_SIZE,
        border=BusinessConstants.QR_CODE_BORDER
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return File(buffer, name=filename)


def generate_equipment_qr_url(inventory_number: str) -> str:
    """
    Generate QR code URL for equipment.

    Args:
        inventory_number: Equipment inventory number

    Returns:
        Full URL for equipment detail page

    Examples:
        >>> generate_equipment_qr_url("INV001")
        'http://localhost:3000/equipment/INV001'
    """
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    return f"{base_url}/equipment/{inventory_number}"


def generate_employee_qr_url(employee_id: str) -> str:
    """
    Generate QR code URL for employee.

    Args:
        employee_id: Employee ID

    Returns:
        Full URL for employee detail page

    Examples:
        >>> generate_employee_qr_url("EMP001")
        'http://localhost:3000/employee/EMP001'
    """
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    return f"{base_url}/employee/{employee_id}"


# ============================================
# OTP Utilities
# ============================================

def generate_otp_code(length: int = BusinessConstants.OTP_CODE_LENGTH) -> str:
    """
    Generate cryptographically secure OTP code.

    Args:
        length: Length of OTP code (default from constants)

    Returns:
        Numeric OTP code as string

    Examples:
        >>> otp = generate_otp_code()
        >>> len(otp)
        6
        >>> otp.isdigit()
        True
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def get_otp_expiry_time() -> datetime:
    """
    Calculate OTP expiry datetime.

    Returns:
        Datetime when OTP should expire

    Examples:
        >>> expiry = get_otp_expiry_time()
        >>> expiry > datetime.now()
        True
    """
    from django.utils import timezone
    return timezone.now() + timedelta(minutes=BusinessConstants.OTP_EXPIRY_MINUTES)


# ============================================
# Date and Time Utilities
# ============================================

def calculate_years_from_date(start_date: date) -> float:
    """
    Calculate years elapsed from given date to today.

    Args:
        start_date: Starting date

    Returns:
        Number of years (including fractional part)

    Examples:
        >>> from datetime import date
        >>> start = date(2020, 1, 1)
        >>> years = calculate_years_from_date(start)
        >>> years > 4.0
        True
    """
    today = date.today()
    days_diff = (today - start_date).days
    return days_diff / 365.25


def calculate_depreciation(
    purchase_price: float,
    purchase_date: date,
    depreciation_rate: float
) -> float:
    """
    Calculate equipment depreciation based on straight-line method.

    Args:
        purchase_price: Original purchase price
        purchase_date: Date when equipment was purchased
        depreciation_rate: Annual depreciation rate (percentage)

    Returns:
        Current value after depreciation

    Examples:
        >>> from datetime import date
        >>> current_value = calculate_depreciation(1000.0, date(2020, 1, 1), 10.0)
        >>> current_value < 1000.0
        True
    """
    years = calculate_years_from_date(purchase_date)
    depreciation = purchase_price * (depreciation_rate / 100) * years
    return max(0, purchase_price - depreciation)


def is_warranty_active(warranty_expiry: Optional[date]) -> bool:
    """
    Check if warranty is still active.

    Args:
        warranty_expiry: Warranty expiry date (None if no warranty)

    Returns:
        True if warranty is active, False otherwise

    Examples:
        >>> from datetime import date, timedelta
        >>> future_date = date.today() + timedelta(days=30)
        >>> is_warranty_active(future_date)
        True
        >>> past_date = date.today() - timedelta(days=30)
        >>> is_warranty_active(past_date)
        False
    """
    if not warranty_expiry:
        return False
    return date.today() <= warranty_expiry


def calculate_days_between(start_date: datetime, end_date: Optional[datetime] = None) -> int:
    """
    Calculate days between two dates.

    Args:
        start_date: Start datetime
        end_date: End datetime (defaults to now if None)

    Returns:
        Number of days

    Examples:
        >>> from django.utils import timezone
        >>> from datetime import timedelta
        >>> start = timezone.now() - timedelta(days=10)
        >>> calculate_days_between(start)
        10
    """
    if end_date is None:
        from django.utils import timezone
        end_date = timezone.now()

    return (end_date - start_date).days


# ============================================
# Image Processing Utilities
# ============================================

def prepare_image_for_upload(image: Image.Image) -> Image.Image:
    """
    Prepare image for upload by converting to RGB and optimizing.

    Handles images with alpha channel (RGBA, LA, P) by converting to RGB.

    Args:
        image: PIL Image object

    Returns:
        Processed PIL Image in RGB mode

    Examples:
        >>> from PIL import Image
        >>> img = Image.open("test.png")
        >>> processed = prepare_image_for_upload(img)
        >>> processed.mode
        'RGB'
    """
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        return background
    return image


# ============================================
# Request Utilities
# ============================================

def get_client_ip(request) -> Optional[str]:
    """
    Extract client IP address from request.

    Handles proxy headers (X-Forwarded-For).

    Args:
        request: Django request object

    Returns:
        Client IP address or None

    Examples:
        >>> ip = get_client_ip(request)
        >>> ip is not None
        True
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request) -> str:
    """
    Extract user agent string from request.

    Args:
        request: Django request object

    Returns:
        User agent string (empty string if not found)

    Examples:
        >>> user_agent = get_user_agent(request)
        >>> isinstance(user_agent, str)
        True
    """
    return request.META.get('HTTP_USER_AGENT', '')


# ============================================
# Data Formatting Utilities
# ============================================

def format_currency(amount: float, currency: str = 'UZS') -> str:
    """
    Format amount as currency string.

    Args:
        amount: Numeric amount
        currency: Currency code (default: UZS)

    Returns:
        Formatted currency string

    Examples:
        >>> format_currency(1000000)
        '1,000,000 UZS'
        >>> format_currency(1234.56)
        '1,234.56 UZS'
    """
    return f"{amount:,.2f} {currency}".replace(',', ' ')


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default

    Examples:
        >>> safe_int("123")
        123
        >>> safe_int("invalid")
        0
        >>> safe_int("invalid", default=-1)
        -1
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default

    Examples:
        >>> safe_float("123.45")
        123.45
        >>> safe_float("invalid")
        0.0
        >>> safe_float("invalid", default=-1.0)
        -1.0
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# ============================================
# Pagination Utilities
# ============================================

def get_page_number(request, param_name: str = 'page') -> int:
    """
    Extract page number from request parameters.

    Args:
        request: Django request object
        param_name: Query parameter name for page

    Returns:
        Page number (1-indexed), defaults to 1

    Examples:
        >>> page = get_page_number(request)
        >>> page >= 1
        True
    """
    return max(1, safe_int(request.query_params.get(param_name, 1)))


def get_page_size(request, param_name: str = 'page_size') -> int:
    """
    Extract page size from request parameters.

    Args:
        request: Django request object
        param_name: Query parameter name for page size

    Returns:
        Page size (limited by MAX_PAGE_SIZE constant)

    Examples:
        >>> size = get_page_size(request)
        >>> 1 <= size <= 100
        True
    """
    size = safe_int(
        request.query_params.get(param_name),
        default=BusinessConstants.DEFAULT_PAGE_SIZE
    )
    return min(size, BusinessConstants.MAX_PAGE_SIZE)


# ============================================
# String Utilities
# ============================================

def generate_serial_number(inventory_number: str, prefix: str = "SN") -> str:
    """
    Generate serial number from inventory number.

    Args:
        inventory_number: Equipment inventory number
        prefix: Serial number prefix

    Returns:
        Generated serial number

    Examples:
        >>> generate_serial_number("INV001")
        'SN-INV001'
        >>> generate_serial_number("INV001", prefix="SERIAL")
        'SERIAL-INV001'
    """
    return f"{prefix}-{inventory_number}"


def truncate_string(text: str, max_length: int = 200, suffix: str = '...') -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        Truncated string

    Examples:
        >>> truncate_string("Hello World", max_length=8)
        'Hello...'
        >>> truncate_string("Hello", max_length=10)
        'Hello'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ============================================
# Audit Helpers
# ============================================

def get_model_changes(old_instance: Any, new_instance: Any, fields: list) -> Dict[str, Dict[str, Any]]:
    """
    Get dictionary of changed fields between two model instances.

    Args:
        old_instance: Original model instance
        new_instance: Updated model instance
        fields: List of field names to check

    Returns:
        Dictionary with field names as keys and {old, new} values

    Examples:
        >>> changes = get_model_changes(old_obj, new_obj, ['name', 'price'])
        >>> 'name' in changes
        True
    """
    changes = {}
    for field in fields:
        old_value = getattr(old_instance, field, None)
        new_value = getattr(new_instance, field, None)

        if old_value != new_value:
            changes[field] = {
                'old': str(old_value),
                'new': str(new_value)
            }

    return changes

def generate_next_inventory_number(prefix: str) -> str:
    """
    Generate next available inventory number with given prefix.
    Format: PREFIX-0001
    
    Args:
        prefix: Prefix string (usually category code)
        
    Returns:
        New unique inventory number
    """
    from .models import Equipment
    import re
    
    # Normalize prefix (uppercase, strip)
    prefix = prefix.upper().strip()
    
    # Find all equipment with this prefix
    # Use exact prefix match with hyphen, e.g. "LAPTOP-"
    search_prefix = f"{prefix}-"
    
    # Get the last equipment with this prefix
    # We filter by length first to ensure correct ordering if possible, 
    # but simplest reliable way is to fetch recent ones and parsing
    last_item = Equipment.objects.filter(
        inventory_number__startswith=search_prefix
    ).order_by('-created_at').first()
    
    next_seq = 1
    
    if last_item:
        # Try to extract sequence number from last item
        # Expected format: PREFIX-0001
        last_inv = last_item.inventory_number
        if last_inv.startswith(search_prefix):
            try:
                suffix = last_inv[len(search_prefix):]
                # Extract digits
                match = re.search(r'(\d+)$', suffix)
                if match:
                    next_seq = int(match.group(1)) + 1
            except (ValueError, IndexError):
                # Fallback if parsing fails
                pass
                
    # Check for collision loop (just in case of race condition or format mix)
    while True:
        new_inv = f"{prefix}-{next_seq:04d}"
        if not Equipment.objects.filter(inventory_number=new_inv).exists():
            return new_inv
        next_seq += 1
