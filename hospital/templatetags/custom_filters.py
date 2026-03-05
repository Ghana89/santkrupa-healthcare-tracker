from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    return str(value).lower().endswith(arg.lower())


@register.filter
def is_image(value):
    return str(value).lower().endswith(('.jpg', '.jpeg', '.png'))

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces"""
    if isinstance(value, str):
        return value.replace('_', ' ')
    return value