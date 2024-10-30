# In your_app/context_processors.py
from django.contrib import admin
from store.models import Notifications


def app_list(request):

    return {
        "app_list": admin.site.get_app_list(request),
        "new_notification": Notifications.objects.filter(seen=False),
        "new_notification_count": Notifications.objects.filter(seen=False).count(),
    }
