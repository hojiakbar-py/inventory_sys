from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, EquipmentCategoryViewSet,
    EquipmentViewSet, AssignmentViewSet, InventoryCheckViewSet,
    MaintenanceRecordViewSet, QRScanViewSet, AuditLogViewSet,
    request_password_change_otp, verify_otp, change_password_with_otp
)
from .auth_views import (
    login_view, register_view, logout_view, user_info_view,
    update_profile_view, change_password_view
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'equipment-categories', EquipmentCategoryViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'inventory-checks', InventoryCheckViewSet)
router.register(r'maintenance-records', MaintenanceRecordViewSet)
router.register(r'qr-scan', QRScanViewSet, basename='qr-scan')
router.register(r'audit-logs', AuditLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Auth endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', user_info_view, name='user-info'),
    path('auth/update-profile/', update_profile_view, name='update-profile'),
    path('auth/change-password/', change_password_view, name='change-password'),
    # OTP endpoints
    path('auth/request-password-change-otp/', request_password_change_otp, name='request-password-change-otp'),
    path('auth/verify-otp/', verify_otp, name='verify-otp'),
    path('auth/change-password-with-otp/', change_password_with_otp, name='change-password-with-otp'),
]
