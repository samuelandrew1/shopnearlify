from django import template
from django.utils.text import format_lazy

register = template.Library()


@register.filter(name="currency_naira")
def currency_naira(value):
    """Formats a number as currency with Naira symbol and thousand separators"""
    try:
        value = float(value)
        formatted_price = "₦{:,.2f}".format(value)
        return formatted_price
    except (ValueError, TypeError):
        return value  # In case of an invalid value, return the original input.
