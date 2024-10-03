# inventory/templatetags/form_tags.py

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    existing_classes = field.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_class}"
    return field.as_widget(attrs={'class': new_classes})
