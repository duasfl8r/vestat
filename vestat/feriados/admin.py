# -*- encoding: utf-8 -*-
"""
Configurações do Django Admin Site pra aplicação `feriados`.
"""

from django.contrib import admin

from models import Feriado

class FeriadoAdmin(admin.ModelAdmin):
    def data(self, f):
        return f.data
    data.short_description = "Data"

    list_display = ["data", "nome"]
    list_display_links = ["data", "nome"]

admin.site.register(Feriado, FeriadoAdmin)
