
from django import template

register = template.Library()

@register.filter
def add_charge(pills):
    total_charge = 0
    for pill in pills :
        total_charge = total_charge + pill.charge()


    return float(total_charge)
    
    
