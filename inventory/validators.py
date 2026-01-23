"""
Custom validators for inventory models.

This module contains all custom validation functions used across the application.
All validators follow Django's validation pattern and raise ValidationError when validation fails.
"""

import os
import re
from typing import Optional

from django.core.exceptions import ValidationError

from .constants import ValidationConstants, ErrorMessages


# ============================================
# String Validators
# ============================================

def validate_inventory_number(value: str) -> None:
    """
    Validate inventory number format and length.

    Args:
        value: Inventory number to validate

    Raises:
        ValidationError: If inventory number is invalid

    Examples:
        >>> validate_inventory_number("INV001")  # Valid
        >>> validate_inventory_number("IN")  # Raises ValidationError
    """
    if not value or len(value.strip()) < ValidationConstants.MIN_INVENTORY_NUMBER_LENGTH:
        raise ValidationError(ErrorMessages.INVALID_INVENTORY_NUMBER)


def validate_employee_id(value: str) -> None:
    """
    Validate employee ID format and length.

    Args:
        value: Employee ID to validate

    Raises:
        ValidationError: If employee ID is invalid

    Examples:
        >>> validate_employee_id("EMP001")  # Valid
        >>> validate_employee_id("EM")  # Raises ValidationError
    """
    if not value or len(value.strip()) < ValidationConstants.MIN_EMPLOYEE_ID_LENGTH:
        raise ValidationError(ErrorMessages.INVALID_EMPLOYEE_ID)


def validate_serial_number(value: Optional[str]) -> None:
    """
    Validate equipment serial number format and length.

    Args:
        value: Serial number to validate (optional)

    Raises:
        ValidationError: If serial number is invalid

    Examples:
        >>> validate_serial_number("SN123456")  # Valid
        >>> validate_serial_number("SN")  # Raises ValidationError
        >>> validate_serial_number(None)  # Valid (optional field)
    """
    if value and len(value.strip()) < ValidationConstants.MIN_SERIAL_NUMBER_LENGTH:
        raise ValidationError(ErrorMessages.INVALID_SERIAL_NUMBER)


# ============================================
# Phone and Document Validators
# ============================================

def validate_phone_number(value: Optional[str]) -> None:
    """
    Validate Uzbekistan phone number format.

    Accepts formats: +998XXXXXXXXX, 998XXXXXXXXX
    Ignores spaces and hyphens in input.

    Args:
        value: Phone number to validate (optional)

    Raises:
        ValidationError: If phone number format is invalid

    Examples:
        >>> validate_phone_number("+998901234567")  # Valid
        >>> validate_phone_number("998 90 123 45 67")  # Valid
        >>> validate_phone_number("+99890123456")  # Raises ValidationError
        >>> validate_phone_number(None)  # Valid (optional field)
    """
    if not value:
        return

    # Remove spaces and hyphens for validation
    cleaned_value = value.replace(' ', '').replace('-', '')

    if not re.match(ValidationConstants.PHONE_PATTERN, cleaned_value):
        raise ValidationError(ErrorMessages.INVALID_PHONE_NUMBER)


def validate_passport_series(value: Optional[str]) -> None:
    """
    Validate Uzbekistan passport series format.

    Expected format: XX1234567 (2 uppercase letters + 7 digits)

    Args:
        value: Passport series to validate (optional)

    Raises:
        ValidationError: If passport series format is invalid

    Examples:
        >>> validate_passport_series("AA1234567")  # Valid
        >>> validate_passport_series("AB123456")  # Raises ValidationError
        >>> validate_passport_series("aa1234567")  # Raises ValidationError
        >>> validate_passport_series(None)  # Valid (optional field)
    """
    if not value:
        return

    if not re.match(ValidationConstants.PASSPORT_PATTERN, value):
        raise ValidationError(ErrorMessages.INVALID_PASSPORT_SERIES)


# ============================================
# Numeric Validators
# ============================================

def validate_positive_price(value: float) -> None:
    """
    Validate that price is non-negative.

    Args:
        value: Price value to validate

    Raises:
        ValidationError: If price is negative

    Examples:
        >>> validate_positive_price(100.50)  # Valid
        >>> validate_positive_price(0)  # Valid
        >>> validate_positive_price(-10)  # Raises ValidationError
    """
    if value < 0:
        raise ValidationError(ErrorMessages.INVALID_PRICE)


def validate_depreciation_rate(value: float) -> None:
    """
    Validate that depreciation rate is within valid range (0-100).

    Args:
        value: Depreciation rate percentage to validate

    Raises:
        ValidationError: If rate is outside valid range

    Examples:
        >>> validate_depreciation_rate(10.5)  # Valid
        >>> validate_depreciation_rate(0)  # Valid
        >>> validate_depreciation_rate(100)  # Valid
        >>> validate_depreciation_rate(101)  # Raises ValidationError
        >>> validate_depreciation_rate(-5)  # Raises ValidationError
    """
    if value < ValidationConstants.MIN_DEPRECIATION_RATE or value > ValidationConstants.MAX_DEPRECIATION_RATE:
        raise ValidationError(ErrorMessages.INVALID_DEPRECIATION_RATE)


# ============================================
# File Validators
# ============================================

def validate_file_size(value) -> None:
    """
    Validate that uploaded file size is within allowed limit.

    Args:
        value: Django UploadedFile object

    Raises:
        ValidationError: If file size exceeds maximum allowed size

    Examples:
        >>> validate_file_size(uploaded_file)  # Valid if < 5MB
        >>> validate_file_size(large_file)  # Raises ValidationError if > 5MB
    """
    if value.size > ValidationConstants.MAX_FILE_SIZE_BYTES:
        raise ValidationError(ErrorMessages.INVALID_FILE_SIZE)


def validate_image_extension(value) -> None:
    """
    Validate that uploaded file has allowed image extension.

    Allowed extensions: jpg, jpeg, png

    Args:
        value: Django UploadedFile object

    Raises:
        ValidationError: If file extension is not allowed

    Examples:
        >>> validate_image_extension(image_file)  # Valid for .jpg, .jpeg, .png
        >>> validate_image_extension(pdf_file)  # Raises ValidationError
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [f'.{ext}' for ext in ValidationConstants.ALLOWED_IMAGE_EXTENSIONS]

    if ext not in valid_extensions:
        raise ValidationError(ErrorMessages.INVALID_IMAGE_EXTENSION)


def validate_document_extension(value) -> None:
    """
    Validate that uploaded file has allowed document extension.

    Allowed extensions: pdf, doc, docx, xls, xlsx

    Args:
        value: Django UploadedFile object

    Raises:
        ValidationError: If file extension is not allowed

    Examples:
        >>> validate_document_extension(pdf_file)  # Valid
        >>> validate_document_extension(image_file)  # Raises ValidationError
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [f'.{ext}' for ext in ValidationConstants.ALLOWED_DOCUMENT_EXTENSIONS]

    if ext not in valid_extensions:
        valid_ext_str = ', '.join(ValidationConstants.ALLOWED_DOCUMENT_EXTENSIONS).upper()
        raise ValidationError(f'Faqat {valid_ext_str} formatdagi hujjatlar qabul qilinadi')


# ============================================
# Composite Validators
# ============================================

def validate_email_or_phone(value: str) -> None:
    """
    Validate that value is either a valid email or phone number.

    Useful for login fields that accept both.

    Args:
        value: String to validate as email or phone

    Raises:
        ValidationError: If value is neither valid email nor phone

    Examples:
        >>> validate_email_or_phone("user@example.com")  # Valid
        >>> validate_email_or_phone("+998901234567")  # Valid
        >>> validate_email_or_phone("invalid")  # Raises ValidationError
    """
    # Try phone validation first
    try:
        validate_phone_number(value)
        return
    except ValidationError:
        pass

    # Try email validation (basic check)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError('Email yoki telefon raqam formatida kiriting')
