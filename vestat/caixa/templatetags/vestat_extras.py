# -*- encoding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.utils.numberformat import format
from django.conf import settings
import datetime
import os

from vestat.django_utils import format_currency

register = template.Library()

@register.filter
def colorir_num(input):
    """Recebe um número e retorna o número marcado com a classe 'pos' se
    for positivo, ou 'neg' se for negativo."""
    try:
        if input > 0:
            s = 'R$ <span class="pos">%s</span>' % (format_currency(input))
        elif input == 0:
            s = 'R$ %s' % (format_currency(input))
        else:
            s = 'R$ <span class="neg">%s</span>' % (format_currency(input))
        return mark_safe(s)
    
    except (ValueError, TypeError):
        return input

@register.filter
def colorir_num_inverso(input):
    """Recebe um número e retorna o número marcado com a classe 'neg' se
    for positivo, ou 'pos' se for negativo -- ou seja, colore ele ao
    contrário do usual.
    
    Usado no mostrador de 10% a pagar -- que é bom se estiver negativo."""
    try:
        if input > 0:
            s = 'R$ <span class="neg">%s</span>' % (format_currency(input))
        elif input == 0:
            s = 'R$ %s' % (format_currency(input))
        else:
            s = 'R$ <span class="pos">%s</span>' % (format_currency(input))
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
