from django.contrib import admin
from .models import (
    Department, Employee, EquipmentCategory, Equipment,
    Assignment, InventoryCheck, MaintenanceRecord, AuditLog
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'position', 'is_active']
    list_filter = ['department', 'is_active', 'position']
    search_fields = ['first_name', 'last_name', 'employee_id']
    readonly_fields = ['qr_code', 'created_at']


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['inventory_number', 'name', 'category', 'status', 'manufacturer', 'model']
    list_filter = ['status', 'category', 'manufacturer']
    search_fields = ['name', 'inventory_number', 'serial_number']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'employee', 'assigned_date', 'return_date', 'assigned_by']
    list_filter = ['assigned_date', 'return_date']
    search_fields = ['equipment__name', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['assigned_date']


@admin.register(InventoryCheck)
class InventoryCheckAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'check_date', 'checked_by', 'is_functional', 'employee_confirmed']
    list_filter = ['is_functional', 'employee_confirmed', 'check_date']
    search_fields = ['equipment__name', 'location']
    readonly_fields = ['check_date']


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'maintenance_type', 'status', 'performed_date', 'performed_by', 'actual_cost']
    list_filter = ['maintenance_type', 'status', 'priority', 'performed_date']
    search_fields = ['equipment__name', 'performed_by', 'description']
    readonly_fields = ['created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp', 'success']
    list_filter = ['action', 'model_name', 'success', 'timestamp']
    search_fields = ['user__username', 'object_repr', 'description']
    readonly_fields = ['user', 'action', 'timestamp', 'content_type', 'object_id', 'model_name',
                      'object_repr', 'changes', 'old_values', 'new_values', 'description',
                      'ip_address', 'user_agent', 'success', 'error_message']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
