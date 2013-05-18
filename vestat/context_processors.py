# -*- encoding: utf-8 -*-
from datetime import datetime
from django.conf import settings

def project_settings(request):
    """
    Adds the project settings to the context.

    """
    return {"project_settings": settings}

def data_hora(request):
    """
    Adiciona a variável `agora` ao contexto, contendo a data-hora atuais
    (objeto `datetime.datetime`)
    """

    return {"agora": datetime.now()}
