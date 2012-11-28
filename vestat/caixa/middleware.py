# -*- encoding: utf-8 -*-
from vestat.contabil.models import Registro
from vestat.caixa import NOME_DO_REGISTRO

from django.contrib.messages.api import info

class AutocreateRegistroMiddleware:
    """
    Cria o registro usado pela app `caixa`, caso não existe.

    """

    def process_request(self, request):
        try:
            Registro.objects.get(nome=NOME_DO_REGISTRO)
        except Registro.DoesNotExist:
            r = Registro(nome=NOME_DO_REGISTRO)
            r.save()
            info(request, "Registro de contabilidade criado")
