from django import template

register = template.Library()
@register.filter
def addActive(path,prefixes):
    for prefix in prefixes.split(","):
        if path.startswith(prefix.strip()):
            return "active"
    return ""
    