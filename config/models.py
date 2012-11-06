"""
Modelos de configuração do Vestat.

"""

from django.db import models

class VestatConfiguration(models.Model):
    """
    Configurações gerais do Vestat.

    Esse modelo deve ser usado como um Singleton -- a única instância
    dele é a definida pela variável `ID_CONFIG` do `settings`.
    """

    class Meta:
            verbose_name = "Configuração do Vestat"
            verbose_name_plural = "Configurações do Vestat"

    # Gorjeta

    saldo_inicial_gorjetas = models.DecimalField("Saldo inicial dos 10%",
            max_digits=10, decimal_places=2, default=0)
    """
    Saldo inicial dos 10%
    """
