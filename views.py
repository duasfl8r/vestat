# -*- encoding: utf-8 -*-
import datetime

from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

import caixa.views

def index(request):
    agora = datetime.datetime.now()
    um_dia = datetime.timedelta(1)

    if agora.hour < 6: # é madrugada, contar como dia anterior
        agora -= um_dia

    intervalo = datetime.timedelta(15)

    antes = agora - intervalo

    # %%2F = barra (/)
    return HttpResponseRedirect("/relatorios/simples/?de=%d%%2F%d%%2F%d&ateh=%d%%2F%d%%2F%d" % (antes.day, antes.month, antes.year,
                                                                                               agora.day, agora.month, agora.year))
