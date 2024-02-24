from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import activate, deactivate_all

register = template.Library()


@register.filter
def arabic_indic(value):
    # Convert numbers to Arabic-Indic numerals
    arabic_numerals = {
        '0': '۰',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩',
    }
    return mark_safe(''.join(arabic_numerals.get(c, c) for c in str(value)))
