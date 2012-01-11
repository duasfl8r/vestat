# -*- encoding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.utils.numberformat import format
from django.conf import settings
import datetime
import os

register = template.Library()

def number_format(number):
    return format(number, settings.DECIMAL_SEPARATOR, 2, grouping=settings.NUMBER_GROUPING, thousand_sep=settings.THOUSAND_SEPARATOR)

@register.filter
def colorir_num(input):
    """Recebe um número e retorna o número marcado com a classe 'pos' se
    for positivo, ou 'neg' se for negativo."""
    try:
        if input > 0:
            s = 'R$ <span class="pos">%s</span>' % (number_format(input))
        elif input == 0:
            s = 'R$ %s' % (number_format(input))
        else:
            s = 'R$ <span class="neg">%s</span>' % (number_format(input))
        return mark_safe(s)
    
    except (ValueError, TypeError):
        return input

UM_DIA = datetime.timedelta(1, 0, 0)

@register.filter
def ontem(input):
    return input - UM_DIA

@register.filter
def amanha(input):
    return input + UM_DIA

@register.filter
def ospathjoin(value, arg):
    return os.path.join(value, arg)
