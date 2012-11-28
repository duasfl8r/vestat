# -*- encoding: utf-8 -*-
"""
Modelos de configuração do Vestat.

"""

from fractions import Fraction

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

    parcelas_10p_casa = models.IntegerField("Parcelas pra casa", default=1,
            help_text="Número de parcelas dos 10% a ser destinada à casa (numerador da fração multiplicadora). Exemplo: 1")
    """
    Parcelas dos 10% destinadas ao restaurante
    """

    parcelas_10p_funcionarios = models.IntegerField("Parcelas pros funcionários", default=3,
            help_text="Número de parcelas dos 10% a ser destinada aos funcionários (numerador da fração multiplicadora). Exemplo: 3")
    """
    Parcelas dos 10% destinadas aos funcionários
    """

    @property
    def _total_de_fatores_10p(self):
        """
        Retorna o denominador das frações de 10% pra casa e pros funcionários.

        Esse denominador é a soma das parcelas pra casa e pros funcionários.

        """

        return self.parcelas_10p_casa + self.parcelas_10p_funcionarios

    @property
    def fracao_10p_casa(self):
        """
        Retorna a razão entre as parcelas pra casa e o total de
        parcelas, como um objeto `fractions.Fraction`.

        """
        return Fraction(self.parcelas_10p_casa, self._total_de_fatores_10p)

    @property
    def fracao_10p_funcionarios(self):
        """
        Retorna a razão entre as parcelas pros funcionários e o total de
        parcelas, como um objeto `fractions.Fraction`.

        """
        return Fraction(self.parcelas_10p_funcionarios, self._total_de_fatores_10p)
