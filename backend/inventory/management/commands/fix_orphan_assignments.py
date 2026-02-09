"""
Management command to find and fix orphan ASSIGNED equipment.

Orphan ASSIGNED equipment = Equipment with status ASSIGNED
but no active Assignment record in the database.

Usage:
    # Faqat tekshirish (o'zgartirmasdan):
    python manage.py fix_orphan_assignments --dry-run

    # Tuzatish (AVAILABLE ga o'zgartirish):
    python manage.py fix_orphan_assignments

    # Barcha ma'lumotlarni ko'rsatish:
    python manage.py fix_orphan_assignments --verbose
"""

from django.core.management.base import BaseCommand
from inventory.models import Equipment, Assignment
from inventory.constants import EquipmentStatus


class Command(BaseCommand):
    help = (
        "Orphan ASSIGNED qurilmalarni topish va tuzatish. "
        "Status ASSIGNED lekin aktiv Assignment yo'q bo'lgan qurilmalarni AVAILABLE ga o'zgartiradi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Faqat tekshirish, hech narsa o'zgartirmaslik",
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help="Batafsil ma'lumot ko'rsatish",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']

        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('Orphan ASSIGNED qurilmalarni tekshirish'))
        self.stdout.write(self.style.NOTICE('=' * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN rejimi — hech narsa o\'zgartirilmaydi'))
        self.stdout.write('')

        # Barcha ASSIGNED statusdagi qurilmalarni topish
        assigned_equipment = Equipment.objects.filter(
            status=EquipmentStatus.ASSIGNED,
            is_active=True,
            is_deleted=False
        )

        total_assigned = assigned_equipment.count()
        self.stdout.write(f"Jami ASSIGNED statusdagi qurilmalar: {total_assigned}")

        orphan_count = 0
        valid_count = 0

        for eq in assigned_equipment:
            active_assignments = Assignment.objects.filter(
                equipment=eq,
                return_date__isnull=True
            )
            active_count = active_assignments.count()

            if active_count == 0:
                # ORPHAN topildi!
                orphan_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  ❌ ORPHAN: {eq.inventory_number} — {eq.name} "
                        f"(Status: ASSIGNED, Aktiv assignment: 0)"
                    )
                )

                if verbose:
                    # Barcha assignmentlarni ko'rsatish
                    all_assignments = Assignment.objects.filter(equipment=eq).order_by('-assigned_date')
                    if all_assignments.exists():
                        for a in all_assignments:
                            self.stdout.write(
                                f"      Assignment: {a.employee.get_full_name()} | "
                                f"Sana: {a.assigned_date} | "
                                f"Qaytarilgan: {a.return_date or 'Yo\'q'}"
                            )
                    else:
                        self.stdout.write("      Hech qanday assignment tarixi yo'q")

                if not dry_run:
                    # Tuzatish: AVAILABLE ga o'zgartirish
                    Equipment.objects.filter(pk=eq.pk).update(status=EquipmentStatus.AVAILABLE)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"      ✅ Status AVAILABLE ga o'zgartirildi"
                        )
                    )
            else:
                valid_count += 1
                if verbose:
                    assignment = active_assignments.first()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ OK: {eq.inventory_number} — {eq.name} "
                            f"→ {assignment.employee.get_full_name()}"
                        )
                    )

        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(f"Natija:")
        self.stdout.write(f"  Jami ASSIGNED: {total_assigned}")
        self.stdout.write(self.style.SUCCESS(f"  To'g'ri (assignment bor): {valid_count}"))

        if orphan_count > 0:
            if dry_run:
                self.stdout.write(
                    self.style.ERROR(
                        f"  Orphan (assignment yo'q): {orphan_count} "
                        f"— tuzatish uchun --dry-run siz ishga tushiring"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Tuzatildi (AVAILABLE ga o'zgartirildi): {orphan_count}"
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("  Orphan topilmadi ✅"))

        self.stdout.write(self.style.NOTICE('=' * 60))
