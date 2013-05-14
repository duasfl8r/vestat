# -*- encoding: utf-8 -*-

"""
Representações dos modelos da app.

"""

from django.contrib import admin
from models import Bandeira
from forms import BandeiraForm



class BandeiraAdmin(admin.ModelAdmin):
    """
    Representação do modelo `Bandeira` no Django admin site.
    """

    list_display = ["ativa", "nome", "taxa", "prazo_de_deposito", "contagem_de_dias", "categoria"]
    list_display_links = ["ativa", "nome"]
    ordering = ["-ativa", "nome"]

    form = BandeiraForm

admin.site.register(Bandeira, BandeiraAdmin)

