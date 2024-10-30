from django import template

register = template.Library()


@register.simple_tag
def star_rating(rating, max_stars=5):
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = max_stars - full_stars - half_star

    stars_html = "★" * full_stars
    if half_star:
        stars_html += (
            "☆"  # Using a different character for half star. Adjust as needed.
        )
    stars_html += "☆" * empty_stars

    return stars_html
