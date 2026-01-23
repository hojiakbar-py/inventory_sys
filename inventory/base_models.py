"""
Base models and mixins for Inventory Management System.

This module provides reusable abstract base classes and mixins that implement
common functionality across models. Using these base classes ensures consistency
and reduces code duplication.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ============================================
# Abstract Base Models
# ============================================

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.

    Automatically tracks when a record was created and last updated.
    Use this as a base for any model that needs timestamp tracking.

    Attributes:
        created_at: DateTime when the record was created (auto-set on creation)
        updated_at: DateTime when the record was last updated (auto-updated on save)

    Example:
        class MyModel(TimeStampedModel):
            name = models.CharField(max_length=100)
            # created_at and updated_at are automatically available
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt",
        help_text="Yozuv yaratilgan vaqt (avtomatik)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="O'zgartirilgan vaqt",
        help_text="Yozuv oxirgi marta o'zgartirilgan vaqt (avtomatik)"
    )

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
        ordering = ['-created_at']


class UserTrackingModel(models.Model):
    """
    Abstract base model that tracks which user created/modified a record.

    Provides fields to track the user who created and last modified a record.
    Useful for audit trails and accountability.

    Attributes:
        created_by: User who created this record
        last_modified_by: User who last modified this record

    Example:
        class MyModel(UserTrackingModel):
            name = models.CharField(max_length=100)
            # created_by and last_modified_by are automatically available
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name="Yaratgan",
        help_text="Ushbu yozuvni yaratgan foydalanuvchi"
    )
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_modified',
        verbose_name="Oxirgi o'zgartirgan",
        help_text="Ushbu yozuvni oxirgi marta o'zgartirgan foydalanuvchi"
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model that implements soft delete functionality.

    Instead of actually deleting records from the database, marks them as deleted.
    This preserves data for audit trails and allows recovery.

    Attributes:
        is_deleted: Whether this record has been soft-deleted
        deleted_at: When the record was soft-deleted
        deleted_by: User who soft-deleted this record

    Methods:
        soft_delete: Mark the record as deleted
        restore: Restore a soft-deleted record
        hard_delete: Permanently delete the record

    Example:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)

        # Usage:
        obj = MyModel.objects.get(id=1)
        obj.soft_delete(user=request.user)  # Soft delete
        obj.restore()  # Restore
        obj.hard_delete()  # Permanently delete
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="O'chirilgan",
        help_text="Ushbu yozuv o'chirilganmi"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="O'chirilgan vaqt",
        help_text="Yozuv o'chirilgan vaqt"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name="O'chirgan",
        help_text="Ushbu yozuvni o'chirgan foydalanuvchi"
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """
        Mark this record as deleted without removing it from the database.

        Args:
            user: User performing the deletion (optional)

        Example:
            obj.soft_delete(user=request.user)
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        """
        Restore a soft-deleted record.

        Example:
            obj.restore()
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    def hard_delete(self):
        """
        Permanently delete this record from the database.

        Warning: This action cannot be undone!

        Example:
            obj.hard_delete()
        """
        super().delete()


class ActiveModel(models.Model):
    """
    Abstract base model that provides active/inactive functionality.

    Allows marking records as active or inactive without deleting them.
    Useful for temporarily disabling records.

    Attributes:
        is_active: Whether this record is currently active

    Methods:
        activate: Mark the record as active
        deactivate: Mark the record as inactive

    Example:
        class MyModel(ActiveModel):
            name = models.CharField(max_length=100)

        # Usage:
        obj = MyModel.objects.get(id=1)
        obj.deactivate()
        obj.activate()
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol",
        help_text="Ushbu yozuv faolmi",
        db_index=True
    )

    class Meta:
        abstract = True

    def activate(self):
        """
        Mark this record as active.

        Example:
            obj.activate()
        """
        self.is_active = True
        self.save()

    def deactivate(self):
        """
        Mark this record as inactive.

        Example:
            obj.deactivate()
        """
        self.is_active = False
        self.save()


class FullAuditModel(TimeStampedModel, UserTrackingModel, ActiveModel):
    """
    Comprehensive audit model combining all common functionality.

    Inherits from:
        - TimeStampedModel: created_at, updated_at
        - UserTrackingModel: created_by, last_modified_by
        - ActiveModel: is_active, activate(), deactivate()

    Use this as a base for models that need complete audit trail functionality.

    Example:
        class Department(FullAuditModel):
            name = models.CharField(max_length=100)
            # Automatically has: created_at, updated_at, created_by,
            # last_modified_by, is_active
    """

    class Meta:
        abstract = True


# ============================================
# Mixins
# ============================================

class QRCodeMixin(models.Model):
    """
    Mixin that adds QR code functionality to a model.

    Provides a QR code image field and abstract method for generating QR code data.
    Subclasses must implement get_qr_code_data() method.

    Attributes:
        qr_code: Image field storing the QR code

    Methods:
        get_qr_code_data: Abstract method to get data for QR code
        generate_qr_code: Generate and save QR code image

    Example:
        class Equipment(QRCodeMixin, models.Model):
            inventory_number = models.CharField(max_length=100)

            def get_qr_code_data(self):
                return f"EQUIPMENT:{self.inventory_number}"
    """
    from django.core.validators import FileExtensionValidator
    from .validators import validate_file_size, validate_image_extension

    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name="QR Kod",
        help_text="Avtomatik yaratilgan QR kod",
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_file_size,
            validate_image_extension
        ]
    )

    class Meta:
        abstract = True

    def get_qr_code_data(self):
        """
        Get the data to encode in the QR code.

        Subclasses must implement this method.

        Returns:
            String data to encode in QR code

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement get_qr_code_data()")

    def generate_qr_code(self):
        """
        Generate QR code image and save it to the qr_code field.

        Uses the data from get_qr_code_data() to create the QR code.

        Example:
            equipment = Equipment.objects.get(id=1)
            equipment.generate_qr_code()
        """
        from .utils import generate_qr_code

        if not self.qr_code:
            qr_data = self.get_qr_code_data()
            filename = f'qr_{self.__class__.__name__.lower()}_{self.pk}.png'
            qr_file = generate_qr_code(qr_data, filename)
            self.qr_code.save(filename, qr_file, save=False)


class NoteMixin(models.Model):
    """
    Mixin that adds a notes/comments field to a model.

    Provides a text field for storing notes, comments, or additional information.

    Attributes:
        notes: Text field for notes

    Example:
        class Equipment(NoteMixin, models.Model):
            name = models.CharField(max_length=100)
            # notes field is automatically available
    """
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Izohlar",
        help_text="Qo'shimcha izohlar va ma'lumotlar"
    )

    class Meta:
        abstract = True


class CodeNameMixin(models.Model):
    """
    Mixin for models that have both a code and a name.

    Provides standardized code and name fields with uniqueness constraints.
    Useful for categorization and reference data models.

    Attributes:
        code: Unique code/identifier
        name: Unique name

    Example:
        class Category(CodeNameMixin, models.Model):
            # code and name are automatically available
            pass
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Kod",
        help_text="Noyob identifikator kod",
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nomi",
        help_text="Noyob nomi"
    )

    class Meta:
        abstract = True

    def __str__(self):
        """String representation showing both code and name."""
        return f"{self.name} ({self.code})"


class DescriptionMixin(models.Model):
    """
    Mixin that adds a description field to a model.

    Provides a text field for storing detailed descriptions.

    Attributes:
        description: Text field for description

    Example:
        class Product(DescriptionMixin, models.Model):
            name = models.CharField(max_length=100)
            # description field is automatically available
    """
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Tavsif",
        help_text="Batafsil tavsif"
    )

    class Meta:
        abstract = True


class LocationMixin(models.Model):
    """
    Mixin that adds location tracking to a model.

    Provides fields for tracking physical location of items or entities.

    Attributes:
        location: Current location
        default_location: Default/assigned location

    Example:
        class Equipment(LocationMixin, models.Model):
            name = models.CharField(max_length=100)
            # location and default_location are automatically available
    """
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Joriy joylashuv",
        help_text="Hozirgi joylashuv"
    )
    default_location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Asosiy joylashuv",
        help_text="Belgilangan asosiy joylashuv"
    )

    class Meta:
        abstract = True
