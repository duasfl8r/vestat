# -*- encoding: utf-8 -*-

from django import template
from ..core import eh_feriado

register = template.Library()
register.filter("eh_feriado", eh_feriado)
