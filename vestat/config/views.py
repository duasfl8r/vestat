# -*- encoding: utf-8 -*-
"""
Views da aplicação `config`
"""

from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext

from core import config_pages


def config_page(request, name):
    """
    Exibe os grupos de links de uma página de configurações, caso ela
    exista; retorna Erro 404 caso ela não exista.

    A página é procurada no dicionário `core.config_pages`; o nome
    fornecido deve ser uma chave desse dicionário, e seu valor
    correspondente deve ser um objeto `core.Page`.

    Argumentos:
        - request
        - name: string; o nome da página de configurações; deve ser uma
          chave do dicionário `core.config_pages`.
    """

    try:
        page = config_pages[name]
    except KeyError:
        raise Http404

    return render_to_response("config_page.html", {
            "page": page,
        },
        context_instance=RequestContext(request))
