# inventory/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(queryset, pk):
    return queryset.get(pk=pk)
