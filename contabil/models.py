# -*- encoding: utf-8 -*-
"""
Modelos de um registro de contabilidade.

Contas
======

A hierarquia de contas é criada conforme vão sendo adicionados
lançamentos.

Cada conta é criada quando é referenciada pela primeira vez.

O nome da conta deve estar no formato `conta:subconta:subconta...`, onde
cada subconta é separada de sua conta-mãe pelo símbolo definido na
variável `contabil.SEPARADOR_DE_CONTAS` (nesse exemplo, dois-pontos).

"""

import datetime
from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

class Registro(models.Model):
    nome = models.TextField(unique=True)

    def balanco(self, conta, de=None, ateh=None):
        """
        Calcula o balanço financeiro de uma conta dentro de um intervalo
        de datas dadas, inclusive.

        Argumentos:

        - conta: um nome de conta seguindo o formato descrito no módulo.
        - de: a data inicial; um objeto `datetime.date`
        - ateh: a data final; um objeto `datetime.date`
        """

        filtros = {}

        if de:
            assert isinstance(de, datetime.date)
            filtros["data__gte"] = de

        if ateh:
            assert isinstance(ateh, datetime.date)
            filtros["data__lte"] = ateh

        resultado = Decimal('0')
        transacoes = self.transacoes.filter(**filtros)

        for transacao in transacoes:
            for lancamento in transacao.lancamentos.all():
                if lancamento.conta == conta:
                    resultado += lancamento.valor

        return resultado

class Transacao(models.Model):
    registro = models.ForeignKey(Registro, related_name="transacoes")
    data = models.DateField("Data")
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    @property
    def eh_consistente(self):
        """
        `True` se os lançamentos da transação somam zero, `False` se não.

        """

        return sum(t.valor for t in self.lancamentos.all()) == 0

    def save(self, *args, **kwargs):
        super(Transacao, self).save(*args, **kwargs)


class Lancamento(models.Model):
    transacao = models.ForeignKey(Transacao, related_name="lancamentos")
    valor = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    conta = models.TextField()

    class Meta:
        verbose_name = "Lançamento"

    def __str__(self):
        return "{conta}: {valor}".format(**vars(self))

    def __unicode__(self):
        return str(self)

    def save(self, *args, **kwargs):
        if self.conta == "":
            raise ValidationError("Campo 'conta' não pode estar vazio!")

        super(Lancamento, self).save(*args, **kwargs)
