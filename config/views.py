# -*- encoding: utf-8 -*-
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from vestat.caixa.models import *
from vestat.config.models import VestatConfiguration
from vestat.config.forms import VestatConfigurationForm
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.core.management import call_command

def index(request):
    config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
    form_config = VestatConfigurationForm(instance=config)

    if request.method == 'POST':
        form_config = VestatConfigurationForm(request.POST, instance=config)
        if form_config.is_valid():
            form_config.save()
            messages.success(request, "Configurações alteradas")
            return redirect(index)

    return render_to_response('config/index.html', {
                                'title': "Configurações",
                                'form_config': form_config,
                                'voltar_link': '/',
                                'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))


def resetar_bd(request):
    if "certeza" in request.GET:
        call_command("reset", "caixa", interactive=False)
        messages.success(request, "O banco de dados foi resetado.")
        return redirect(index)
    
    return render_to_response('config/resetar_bd.html', {
                                'title': "Resetar Banco de Dados",
                                'voltar_link': '/config/',
                                'voltar_label': 'Configurações',
                             },
                             context_instance=RequestContext(request))

def exportar(request):
    response = HttpResponse(Dia.exportar(), mimetype='text/plain')
    response['Content-Disposition'] = "attachment; filename=%s.json" % (settings.NOME_APLICACAO,)
    return response
