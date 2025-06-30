from django import template
from datetime import datetime
from dateutil.relativedelta import relativedelta

register = template.Library()

@register.filter
def is_image(file_type):
    return file_type.startswith("image") if file_type else False


@register.filter
def strip_leading_slash(value):
    if isinstance(value, str):
        return value.lstrip('/')
    return value

@register.simple_tag
def next_12_months():
    months = []
    current = datetime.now()
    for i in range(12):
        future = current + relativedelta(months=i)
        months.append({
            "value": future.strftime("%B %Y"),
            "label": future.strftime("%B %Y"),
        })
    return months

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
