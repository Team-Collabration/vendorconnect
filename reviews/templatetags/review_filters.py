from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return 0
    try:
        return dictionary.get(int(key), 0)
    except (ValueError, TypeError, AttributeError):
        return 0