from django import template
from store.models import Category

register = template.Library()


@register.filter(name="to_int")
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0  # or you can return None or some other default value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_trending_products(trending_products_by_category, category_slug):
    return trending_products_by_category.get(category_slug, {})


@register.simple_tag
def get_categories():
    return Category.objects.all()


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""


@register.filter(name="add_class")
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
