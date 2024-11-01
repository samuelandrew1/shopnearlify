# Generated by Django 4.2.9 on 2024-10-10 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site_logo",
                    models.ImageField(blank=True, null=True, upload_to="site_logo/"),
                ),
                (
                    "contact_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "verbose_name": "Site Setting",
                "verbose_name_plural": "Site Settings",
            },
        ),
    ]
