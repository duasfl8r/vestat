# -*- encoding: utf-8 -*-

"""
Representações dos modelos da app.

"""

import django.forms
from django.db import models
from django.contrib import admin

from models import Registro, Transacao, Lancamento

from vestat.django_utils import LocalizedModelForm
from vestat.caixa import NOME_DO_REGISTRO

class RegistroAdmin(admin.ModelAdmin):
    """
    Representação do modelo `Registro` no Django admin site.

    """

    pass

admin.site.register(Registro, RegistroAdmin)

class LancamentoForm(LocalizedModelForm):
    """
    Formulário de edição do modelo `Lancamento`.

    Esse formulário é *localized* -- a formatação dos números e de
    outros elementos é sensível à língua configurada no sistema.

    """

    class Meta:
        model = Lancamento

class LancamentoInline(admin.TabularInline):
    """
    Representação *inline* do modelo `Lancamento` no Django admin site.

    Permite criar/editar os lançamentos de um objeto `Transacao` na
    própria tela de edição do objeto no admin.

    """

    model = Lancamento
    form = LancamentoForm
    extra = 4

    formfield_overrides = {
        models.TextField: {
            "widget": django.forms.widgets.TextInput(attrs={"size": "40"}),
        },
    }
    """
    Sobrescreve alguns dos campos padrões do formulário.

    """

class TransacaoForm(LocalizedModelForm):
    """
    Formulário de edição do modelo `Lancamento`.

    Esse formulário é *localized* -- a formatação dos números e de
    outros elementos é sensível à língua configurada no sistema.

    """

    class Meta:
        model = Transacao

    registro = django.forms.ModelChoiceField(
        queryset=Registro.objects.all(),
        initial=Registro.objects.get(nome=NOME_DO_REGISTRO),
    )
    """
    Seleciona o registro automaticamente a partir do nome configurado na app `caixa`.

    """


class TransacaoAdmin(admin.ModelAdmin):
    def contas_envolvidas(self, transacao):
        """
        Retorna uma string contendo os nomes das contas envolvidas em
        uma transação, entre aspas e separadas por vírgula.

        """

        return '"' + '", "'.join({ l.conta for l in transacao.lancamentos.all() }) + '"'

    list_display = ["data", "descricao", "contas_envolvidas"]
    search_fields = ["descricao"]
    list_filter = ["data", "lancamentos__conta", "lancamentos__valor"]
    form = TransacaoForm

    inlines = [
        LancamentoInline,
    ]

    class Media:
        css = { "all" : ("css/hide_admin_original.css",) }
        """
        Esconde a representação ``str`` dos objetos `Lancamento`
        *inline* na tela de edição de `Transacao`.

        """

admin.site.register(Transacao, TransacaoAdmin)

class LancamentoAdmin(admin.ModelAdmin):
    """
    Representação do modelo `Lancamento` no Django admin site.

    """

    list_display = ["transacao", "valor", "conta"]

admin.site.register(Lancamento, LancamentoAdmin)
