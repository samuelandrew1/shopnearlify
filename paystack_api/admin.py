from django.contrib import admin
from django.utils.html import format_html
from datetime import datetime, timedelta
from .models import Payment
from django.db import models
from datetime import date, timedelta
from django.contrib.admin import SimpleListFilter
from django.db.models import Sum


class DailyFilter(SimpleListFilter):
    title = "daily"
    parameter_name = "daily"

    def lookups(self, request, model_admin):
        return (("today", "Today"),)

    def queryset(self, request, queryset):
        if self.value() == "today":
            return queryset.filter(date_created__date=date.today())


class WeeklyFilter(SimpleListFilter):
    title = "weekly"
    parameter_name = "weekly"

    def lookups(self, request, model_admin):
        return (("this_week", "This Week"),)

    def queryset(self, request, queryset):
        if self.value() == "this_week":
            start_of_week = date.today() - timedelta(days=date.today().weekday())
            return queryset.filter(date_created__date__gte=start_of_week)


class MonthlyFilter(SimpleListFilter):
    title = "monthly"
    parameter_name = "monthly"

    def lookups(self, request, model_admin):
        return (("this_month", "This Month"),)

    def queryset(self, request, queryset):
        if self.value() == "this_month":
            return queryset.filter(date_created__month=date.today().month)


class AnnualFilter(SimpleListFilter):
    title = "annually"
    parameter_name = "annually"

    def lookups(self, request, model_admin):
        return (("this_year", "This Year"),)

    def queryset(self, request, queryset):
        if self.value() == "this_year":
            return queryset.filter(date_created__year=date.today().year)


import logging


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "ref",
        "email",
        "verified",
        "date_created",
    )
    list_filter = (
        "verified",
        "date_created",
    )
    search_fields = ("user__username", "ref", "email")


def changelist_view(self, request, extra_context=None):
    extra_context = extra_context or {}

    # Get the ChangeList object, which applies all filters to the queryset
    response = super().changelist_view(request, extra_context=extra_context)
    try:
        # Access the queryset from the ChangeList, where all filters have been applied
        cl = response.context_data["cl"]
        queryset = cl.queryset

        # Calculate the sum of the 'amount' field for the filtered queryset
        total_amount = queryset.aggregate(total=Sum("amount"))["total"] or 0

        # Determine the active filter from request.GET (if any)
        filter_type = "All"
        if "date_created__gte" in request.GET and "date_created__lte" in request.GET:
            filter_type = "Date Range"
        # Add other conditions if needed

        # Add the total amount and filter type to the context
        extra_context["filtered_total_amount"] = total_amount
        extra_context["filter_type"] = filter_type
    except (AttributeError, KeyError):
        # Handle cases where the ChangeList object or queryset isn't available
        extra_context["filtered_total_amount"] = 0
        extra_context["filter_type"] = "All"

    return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Payment, PaymentAdmin)
