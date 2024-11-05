from django import template

register = template.Library()

@register.filter
def is_image(file_type):
    return file_type.startswith("image") if file_type else False
