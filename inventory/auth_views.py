from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    """Login API endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Foydalanuvchi nomi va parolni kiriting'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })
        else:
            return Response(
                {'error': 'Foydalanuvchi faol emas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'error': 'Foydalanuvchi nomi yoki parol noto\'g\'ri'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    """Register API endpoint"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    # Validation
    if not username or not email or not password:
        return Response(
            {'error': 'Foydalanuvchi nomi, email va parol majburiy'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(username) < 3:
        return Response(
            {'error': 'Foydalanuvchi nomi kamida 3 ta belgidan iborat bo\'lishi kerak'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'Parol kamida 8 ta belgidan iborat bo\'lishi kerak'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Bu email allaqachon ro\'yxatdan o\'tgan'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create token for auto-login
        token = Token.objects.create(user=user)

        logger.info(f"New user registered: {username}")

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz'
        }, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response(
            {'error': 'Ushbu foydalanuvchi nomi yoki email allaqachon mavjud'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'Ro\'yxatdan o\'tishda xatolik yuz berdi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def logout_view(request):
    """Logout API endpoint"""
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'message': 'Muvaffaqiyatli chiqish amalga oshirildi'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': 'Chiqishda xatolik yuz berdi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def user_info_view(request):
    """Get current user info"""
    user = request.user
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })


@api_view(['PATCH'])
def update_profile_view(request):
    """Update user profile"""
    user = request.user

    # Update allowed fields
    if 'email' in request.data:
        email = request.data['email']
        # Check if email already exists (for other users)
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            return Response(
                {'error': 'Bu email allaqachon boshqa foydalanuvchi tomonidan ishlatilmoqda'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.email = email

    if 'first_name' in request.data:
        user.first_name = request.data['first_name']

    if 'last_name' in request.data:
        user.last_name = request.data['last_name']

    try:
        user.save()
        logger.info(f"User {user.username} updated profile")

        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'message': 'Profil muvaffaqiyatli yangilandi'
        })
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response(
            {'error': 'Profilni yangilashda xatolik'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def change_password_view(request):
    """Change user password"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response(
            {'error': 'Joriy va yangi parolni kiriting'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check old password
    if not user.check_password(old_password):
        return Response(
            {'error': 'Joriy parol noto\'g\'ri'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate new password
    if len(new_password) < 8:
        return Response(
            {'error': 'Yangi parol kamida 8 ta belgidan iborat bo\'lishi kerak'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user.set_password(new_password)
        user.save()

        # Delete old token and create new one
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)

        logger.info(f"User {user.username} changed password")

        return Response({
            'message': 'Parol muvaffaqiyatli o\'zgartirildi',
            'token': new_token.key  # Return new token
        })
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return Response(
            {'error': 'Parolni o\'zgartirishda xatolik'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )