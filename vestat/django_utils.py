# -*- encoding: utf-8 -*-

"""
Classes e funções utilitárias que dependem do Django.
"""

import os
import locale
import tempfile

from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
import django.forms

locale.setlocale(locale.LC_ALL, settings.PYTHON_LOCALE)

class LocalizedModelForm(django.forms.ModelForm):
    """
    Estende o `ModelForm` do django, tornando os campos `DecimalField`
    *localized* -- com a formatação dependente do *locale* do sistema.

    """

    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelForm, cls).__new__(cls, *args, **kwargs)
        for field in new_class.base_fields.values():
            if isinstance(field, django.forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True
        return new_class


def criar_superusuario():
    """
    Cria um superusuário de acordo com as configurações de
    `settings.AUTOLOGIN_USERNAME` e `settings.AUTOLOGIN_PASSWORD`.
    """

    try:
        superuser = User.objects.get(username=settings.AUTOLOGIN_USERNAME)
    except User.DoesNotExist:
        call_command('createsuperuser', interactive=False, username=settings.AUTOLOGIN_USERNAME, email="dev@lucasteixeira.com")
        superuser = User.objects.get(username=settings.AUTOLOGIN_USERNAME)
        superuser.set_password(settings.AUTOLOGIN_PASSWORD)
        superuser.save()


def format_currency(f):
    """
    Formata um número `float` segundo o locale definido no settings, com duas casas decimais.
    """
    return locale.format("%.2f", f).decode("utf-8")


def format_date(d):
    return "{:%d/%m/%Y}".format(d)

def mkstemp(*args, **kwargs):
    if "dir" not in kwargs:
        kwargs["dir"] = os.path.join(settings.MEDIA_ROOT, "tmp")

    return tempfile.mkstemp(*args, **kwargs)

def temp_path2url(path):
    return u"{media}tmp/{basename}".format(
        media=settings.MEDIA_URL,
        basename=os.path.split(path)[-1],
    )
