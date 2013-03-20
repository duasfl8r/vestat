# -*- encoding: utf-8 -*-

"""
Representações dos modelos da app.

"""

from django.contrib import admin
from models import Bandeira



class BandeiraAdmin(admin.ModelAdmin):
    """
    Representação do modelo `Bandeira` no Django admin site.
    """

    list_display = ["nome", "taxa", "prazo_de_deposito", "contagem_de_dias", "categoria"]

admin.site.register(Bandeira, BandeiraAdmin)

