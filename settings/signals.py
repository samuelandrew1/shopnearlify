# signals.py in your app
from django.db.models.signals import post_migrate
from django.conf import settings
from django.db import connection
from .models import SiteSettings


def update_jazzmin_settings(sender, **kwargs):
    # Only update settings if the tables are available in the database
    if connection.introspection.table_names():
        setting = SiteSettings.objects.first()
        if setting:
            settings.JAZZMIN_SETTINGS["site_logo"] = (
                setting.site_logo.url if setting.site_logo else None
            )
            settings.JAZZMIN_SETTINGS["site_brand"] = setting.site_name


# Connect the signal to post_migrate
post_migrate.connect(update_jazzmin_settings)
