# -*- encoding: utf-8 -*-

from django.db import models
from django.forms.widgets import TextInput
from django.contrib import admin

from models import Registro, Transacao, Lancamento

class RegistroAdmin(admin.ModelAdmin):
    pass

admin.site.register(Registro, RegistroAdmin)

class LancamentoInline(admin.TabularInline):
    model = Lancamento
    extra = 4

    formfield_overrides = {
        models.TextField: {
            "widget": TextInput(attrs={"size": "40"}),
        },
    }

class TransacaoAdmin(admin.ModelAdmin):
    list_display = ["data", "descricao"]
    search_fields = ["descricao"]
    list_filter = ["data", "lancamentos__conta", "lancamentos__valor"]

    inlines = [
        LancamentoInline,
    ]

    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

admin.site.register(Transacao, TransacaoAdmin)

class LancamentoAdmin(admin.ModelAdmin):
    list_display = ["transacao", "valor", "conta"]

admin.site.register(Lancamento, LancamentoAdmin)
