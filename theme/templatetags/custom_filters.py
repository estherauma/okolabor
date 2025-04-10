from django import template

register = template.Library()

@register.filter
def is_image(file_type):
    return file_type.startswith("image") if file_type else False


@register.filter
def strip_leading_slash(value):
    if isinstance(value, str):
        return value.lstrip('/')
    return value