from django.contrib import admin
from django.utils.html import format_html


from .models import SiteSettings


# from django_inline_actions.admin import InlineActionsMixin

# from django.contrib import admin

# from .models import SiteSettings

# @admin.register(SiteSettings)
# class SiteSettingsAdmin(InlineActionsMixin, admin.ModelAdmin):
#     list_display = ('site_logo', 'contact_number', 'email')

#     def get_inline_actions(self, request, obj=None):
#         actions = super(SiteSettingsAdmin, self).get_inline_actions(request, obj)
#         actions.append('delete')  # Add custom delete action
#         return actions

#     def delete(self, request, obj, parent_obj=None):
#         """ Custom delete action """
#         obj.delete()
#         self.message_user(request, f"{obj} deleted successfully")


@admin.register(
    SiteSettings,
)
class SiteSettingsAdmin(admin.ModelAdmin):

    def logo(self, obj):
        return format_html(
            '<img src="{}" style="max-width:50px; max-height:100px"/>'.format(
                obj.site_logo.url
            )
        )

    list_display = ("contact_number", "email", "address", "logo")

    # Optional: Restrict admin to edit only one settings entry
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
