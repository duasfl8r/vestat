# -*- encoding: utf-8 -*-

import django.forms
from django.db import models
from django.contrib import admin

from models import Registro, Transacao, Lancamento

from vestat.utils import LocalizedModelForm

class RegistroAdmin(admin.ModelAdmin):
    pass

admin.site.register(Registro, RegistroAdmin)

class LancamentoForm(LocalizedModelForm):
    class Meta:
        model = Lancamento

class LancamentoInline(admin.TabularInline):
    model = Lancamento
    form = LancamentoForm
    extra = 4

    formfield_overrides = {
        models.TextField: {
            "widget": django.forms.widgets.TextInput(attrs={"size": "40"}),
        },
    }

class TransacaoForm(LocalizedModelForm):
    class Meta:
        model = Transacao


class TransacaoAdmin(admin.ModelAdmin):
    list_display = ["data", "descricao"]
    search_fields = ["descricao"]
    list_filter = ["data", "lancamentos__conta", "lancamentos__valor"]
    form = TransacaoForm

    inlines = [
        LancamentoInline,
    ]

    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }

admin.site.register(Transacao, TransacaoAdmin)

class LancamentoAdmin(admin.ModelAdmin):
    list_display = ["transacao", "valor", "conta"]

admin.site.register(Lancamento, LancamentoAdmin)
