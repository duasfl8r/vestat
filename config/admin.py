# -*- encoding: utf-8 -*-

"""
Representações dos modelos de configuração do Vestat no Django admin site.

"""

from django.contrib import admin

from vestat.config.models import VestatConfiguration

class VestatConfigurationAdmin(admin.ModelAdmin):
    """
    Representação do modelo `VestatConfiguration` no Django admin site.

    """

    fracao_10p_casa = lambda c: c.fracao_10p_casa
    fracao_10p_casa.short_description = "Fração dos 10% pra casa"

    fracao_10p_funcionarios = lambda c: c.fracao_10p_funcionarios
    fracao_10p_funcionarios.short_description = "Fração dos 10% pros funcionários"

    list_display = ["id", fracao_10p_casa, fracao_10p_funcionarios]
    """
    Campos a serem exibidos na listagem de objetos `VestatConfiguration`.

    Exibe, além do ID do objeto, a fração dos 10% destinada à casa
    e a fração destinada aos funcionários.

    """

    fieldsets = [
        ("10%",
            {
                "fields": ["parcelas_10p_casa", "parcelas_10p_funcionarios"],
                "description": "A soma das parcelas pra casa e pros funcionários será o denominador da fração multiplicadora."
            }
        ),

    ]
    """
    Campos a serem exibidos no formulário de criação/edição de configuração.

    """

admin.site.register(VestatConfiguration, VestatConfigurationAdmin)
