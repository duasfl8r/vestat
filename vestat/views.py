# -*- encoding: utf-8 -*-
import sys
import datetime
from traceback import format_tb

from django.shortcuts import redirect, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError

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

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name)
    ltype, lvalue, ltraceback = sys.exc_info()
    sys.exc_clear()
    traceback = "".join(format_tb(ltraceback))
    return HttpResponseServerError(t.render(RequestContext(request, {
        "traceback": traceback,
        "type": ltype,
        "value": lvalue,
    })))
