# -*- encoding: utf-8 -*-
import logging
import traceback
import pprint

from django.core.management import call_command
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.messages.api import info
from django.contrib.auth import authenticate, login

from vestat.config.models import VestatConfiguration
from vestat.django_utils import criar_superusuario


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
            criar_superusuario()
            info(request, "Superusuário criado.")

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
        error_data = [u"URL: " + request.path + "\n",
                      traceback.format_exc().decode("utf-8"),
                      u"GET:\n" + pprint.pformat(request.GET),
                      u"POST:\n" + pprint.pformat(request.POST),
                      ]
        error_msg = u"\n".join(error_data)
        logger.error(error_msg)

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
                logger.warn("User {username} is not active".format(**kwargs))
        else:
            logger.warn("Cannot login {username} using password {password}".format(**kwargs))
