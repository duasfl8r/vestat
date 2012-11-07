# -*- encoding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError

from contabil import SEPARADOR_DE_CONTAS

class Registro(models.Model):
    nome = models.TextField(unique=True)

class Transacao(models.Model):
    registro = models.ForeignKey(Registro, related_name="transacoes")
    data = models.DateField("Data")
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    def save(self, *args, **kwargs):
        if sum(t.valor for t in self.lancamentos.all()) != 0:
            raise ValidationError("A soma dos lançamentos de uma transação devem ter soma 0")
        super(Transacao, self).save(*args, **kwargs)


class Lancamento(models.Model):
    transacao = models.ForeignKey(Transacao, related_name="lancamentos")
    valor = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    conta = models.TextField()
    """
    O caminho devem estar no formato
    `conta:subconta:subconta...`, onde cada subconta é separada
    de sua conta-mãe pelo símbolo definido na variável global
    `SEPARADOR_DE_CONTAS` (nesse exemplo, dois-pontos).

    """

    class Meta:
        verbose_name = "Lançamento"

    def __str__(self):
        return "{conta}: {valor}".format(**vars(self))

    def __unicode__(self):
        return str(self)


