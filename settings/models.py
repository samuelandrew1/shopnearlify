# Register your models here.
from django.db import models


class SiteSettings(models.Model):
    site_logo = models.ImageField(upload_to="site_logo/", blank=True, null=True)
    profile_picture = models.ImageField(upload_to="site_logo/", blank=True, null=True)
    site_name = models.CharField(max_length=100, default="My Site")
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twiter_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
