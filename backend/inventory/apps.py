from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        # Make User email field unique
        from django.contrib.auth.models import User
        email_field = User._meta.get_field('email')
        email_field._unique = True
