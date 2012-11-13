# -*- encoding: utf-8 -*-

from django.contrib import admin

from vestat.config.models import VestatConfiguration

class VestatConfigurationAdmin(admin.ModelAdmin):
    fracao_10p_casa = lambda c: c.fracao_10p_casa
    fracao_10p_casa.short_description = "Fração dos 10% pra casa"

    fracao_10p_funcionarios = lambda c: c.fracao_10p_funcionarios
    fracao_10p_funcionarios.short_description = "Fração dos 10% pros funcionários"

    list_display = ["id", fracao_10p_casa, fracao_10p_funcionarios]

    fieldsets = [
        ("10%",
            {
                "fields": ["parcelas_10p_casa", "parcelas_10p_funcionarios"],
                "description": "A soma das parcelas pra casa e pros funcionários será o denominador da fração multiplicadora."
            }
        ),

    ]

admin.site.register(VestatConfiguration, VestatConfigurationAdmin)
