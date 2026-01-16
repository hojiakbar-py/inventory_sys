"""
Management command to send warranty expiration alerts
Usage: python manage.py send_warranty_alerts
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from inventory.models import Equipment
from decouple import config


class Command(BaseCommand):
    help = 'Send email alerts for equipment with expiring warranties'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days before expiry to send alert (default: 30)',
        )

    def handle(self, *args, **options):
        days_before = options['days']
        today = timezone.now().date()
        alert_date = today + timedelta(days=days_before)

        self.stdout.write(f"Checking warranties expiring in the next {days_before} days...")

        # Find equipment with expiring warranties
        expiring_equipment = Equipment.objects.filter(
            warranty_expiry__lte=alert_date,
            warranty_expiry__gte=today,
            status__in=['AVAILABLE', 'ASSIGNED']
        ).select_related('category', 'created_by')

        if not expiring_equipment.exists():
            self.stdout.write(self.style.SUCCESS('No warranties expiring soon.'))
            return

        self.stdout.write(f"Found {expiring_equipment.count()} equipment with expiring warranties")

        # Group by warranty expiry date
        alerts_sent = 0
        for equipment in expiring_equipment:
            days_left = (equipment.warranty_expiry - today).days

            # Email subject and message
            subject = f'Warranty Expiring Soon: {equipment.name}'
            message = f"""
Kafolat Muddati Tugashi Haqida Ogohlantirish

Qurilma: {equipment.name}
Kategoriya: {equipment.category.name if equipment.category else 'N/A'}
Inventar raqami: {equipment.inventory_number}
Seriya raqami: {equipment.serial_number}

Kafolat muddati: {equipment.warranty_expiry}
Qolgan kunlar: {days_left} kun

Kafolat beruvchi: {equipment.warranty_provider or 'N/A'}

Holati: {equipment.get_status_display()}

Iltimos, kerakli choralarni ko'ring.

---
Inventarizatsiya Tizimi
            """

            # Get recipient email
            recipient_email = config('ADMIN_EMAIL', default='admin@inventory.com')

            try:
                send_mail(
                    subject,
                    message,
                    config('DEFAULT_FROM_EMAIL', default='noreply@inventory.com'),
                    [recipient_email],
                    fail_silently=False,
                )
                alerts_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Alert sent for {equipment.name} ({days_left} days left)')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to send alert for {equipment.name}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nCompleted! {alerts_sent}/{expiring_equipment.count()} alerts sent.')
        )
