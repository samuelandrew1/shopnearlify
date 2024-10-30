from .models import SiteSettings


def site_settings(request):
    settings = (
        SiteSettings.objects.first()
    )  # Get the first and only instance of SiteSettings
    return {
        "site_settings": settings,  # Make this available in all templates
        "site_logo": (
            settings.site_logo.url if settings and settings.site_logo else None
        ),
        "profile_image": (
            settings.profile_picture.url
            if settings and settings.profile_picture
            else None
        ),
        "site_brand": settings.site_name if settings else "My Admin",
    }
