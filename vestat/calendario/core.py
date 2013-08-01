# -*- encoding: utf-8 -*-
"""
Núcleo da aplicação de calendário.

Como usar esse módulo
---------------------

A função `get_events`, usada pra puxar os eventos exibidos no
calendário, procura por geradores de eventos em todas as aplicações
instaladas em `settings.INSTALLED_APPS`.

Pra criar um gerador de eventos:

1. Dentro da aplicação django, crie um módulo `events.py`.

2. Dentro desse módulo, crie uma função com as seguintes características:
    - o nome deve terminar em `events`
    - deve receber dois parâmetros: uma data de início e uma data de
      fim, ambos objetos `datetime.date`.
    - deve retornar uma sequência (list, tuple) ou gerador com objetos
      `Event` cuja data esteja entre as datas fornecidas, inclusive.
"""

import logging
from django.conf import settings

logger = logging.getLogger("vestat")

class Event():
    """
    Um evento de calendário.
    """
    def __init__(self, date, text, description=None):
        """
        Inicializa o evento.

        Argumentos:

        - date: um objeto `datetime.date`; a data do evento
        - text: uma string; o título do evento
        - description: uma string ou `None`; a descrição do evento; se
          for passado `None` (ie o argumento não for passado), a
          descrição é a string vazia.
        """
        self.date = date
        self.text = text
        self.description = description if description else ""

    def __unicode__(self):
        return u"{date} - {text}".format(**vars(self))

def get_events(begin, end):
    """
    Retorna os eventos, de todos os aplicativos instalados, que
    aconteçam entre as duas datas fornecidas, inclusive.

    Para cada aplicação `app` instalada em `settings.INSTALLED_APPS`,
    procura-se um módulo `app.events`; caso ele exista, puxa todas as
    variáveis desse módulo que terminem em 'events' e os chama como
    geradores de eventos.

    Finalmente, retorna todos os eventos gerados por ordem crescente de
    data.

    Argumentos:

    - begin: objeto `datetime.date`; data de início da busca
    - end: objeto `datetime.date`; data de fim da busca
    """

    event_list = []

    for app in settings.INSTALLED_APPS:
        events_module_name = app + ".events"

        try:
            module = __import__(events_module_name, fromlist=["events"])
        except ImportError:
            pass
        else:
            generators = [i for i in vars(module).items() if i[0].endswith("events")]

            for name, function in generators:
                result = list(function(begin, end))
                event_list.extend(result)

    return sorted(event_list, key=lambda e: e.date)
