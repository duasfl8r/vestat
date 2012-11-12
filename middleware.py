# -*- encoding: utf-8 -*-
from django.core.management import call_command
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.messages.api import info
from django.contrib.auth import authenticate, login

from vestat.config.models import VestatConfiguration

import logging
import traceback
import pprint


logger = logging.getLogger(settings.NOME_APLICACAO)

class AutocreateDatabaseMiddleware():
    def process_request(self, request):
        try:
            db_name = settings.DATABASES['default']['NAME']
            db = open(db_name)
            db.close()
        except IOError:
            call_command("syncdb", interactive=False)
            info(request, "Banco de dados criado.")

class AutocreateConfigMiddleware():
    def process_request(self, request):
        try:
            config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
        except VestatConfiguration.DoesNotExist:
            config = VestatConfiguration(id=settings.ID_CONFIG)
            config.save()
            info(request, "Configuração criada.")


class ExceptionLoggerMiddleware():
    """Logs exceptions in a file."""

    def process_exception(self, request, exception):
        error_data = ["URL: " + request.path + "\n",
                      traceback.format_exc(),
                      "GET:\n" + pprint.pformat(request.GET),
                      "POST:\n" + pprint.pformat(request.POST),
                      "META:\n" + pprint.pformat(request.META),
                      ]
        error_msg = "\n".join(error_data)
        logger.error(error_msg)

        return render_to_response('500.html', {
                                  'settings': settings,
                                 },
                                 context_instance=RequestContext(request))

class AutologinMiddleware():
    """
    Faz login automático.

    Como o Vestat é uma aplicação Desktop, sem comunicação externa, a
    autenticação necessária pra usar o Django Admin é inconveniente.

    """

    def process_request(self, request):
        kwargs =  {
            "username": settings.AUTOLOGIN_USERNAME,
            "password": settings.AUTOLOGIN_PASSWORD
        }

        user = authenticate(**kwargs)

        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                logger.warn("User {user} is not active".format(**kwargs))
        else:
            logger.warn("Cannot login {user} using password {password}".format(**kwargs))
