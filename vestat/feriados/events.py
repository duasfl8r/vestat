# -*- encoding: utf-8 -*-
"""
Geradores de eventos da aplicação `feriados`.

Funções se comportam de acordo com o esperado pela aplicação
`calendario`.
"""

from vestat.calendario import Event

from core import feriados_entre

def feriados_events(begin, end):
    """
    Eventos pros feriados.
    """

    for data, feriado in feriados_entre(begin, end):
        yield Event(data, u"Feriado: {0}".format(feriado.nome))
