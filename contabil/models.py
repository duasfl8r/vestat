# -*- encoding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError

SEPARADOR_DE_CONTAS = ":"

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
        if sum(t.valor for t in self.transferencias.all()) != 0:
            raise ValidationError("A soma das transferências de uma transação devem ter soma 0")
        super(Transacao, self).save(*args, **kwargs)


class Transferencia(models.Model):
    transacao = models.ForeignKey(Transacao, related_name="transferencias")
    valor = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    origem = models.TextField(blank=False)
    destino = models.TextField(blank=False)

    class Meta:
        verbose_name = "Transferência"
        verbose_name_plural = "Transferências"

    def __str__(self):
        return "{valor} ({origem} -> {destino})".format(**vars(self))

    def __unicode__(self):
        return str(self)



class Contas:
    """
    Fornece métodos para construir e inquirir uma hierarquia de contas
    financeiras.

    """

    def __init__(self):
        self._hierarquia = {
            "transferencias": [],
            "contas": {},
        }

    def digerir_registro(self, registro):
        """
        Alimenta o objeto com contas tiradas de um registro de
        transações.

        Argumentos:

        - registro: objeto `Registro`.

        """

        self.digerir_transacoes(registro.transacoes.all())

    def digerir_transacoes(self, transacoes):
        """
        Alimenta o objeto com contas tiradas de transações.

        Argumentos:

        - transacoes: um iterable contendo objetos `Transacao`.

        """

        resultado = {}

        for transacao in transacoes:
            self.digerir_transferencias(transacao.transferencias.all())

    def digerir_transferencias(self, transferencias):
        """
        Alimenta o objeto com contas tiradas de transferências.

        Argumentos:

        - transferencias: um iterable contendo objetos `Transferencia`.

        """

        resultado = {}

        for transferencia in transferencias:
            for caminho in [transferencia.origem, transferencia.destino]:
                self._digerir_caminho(caminho, transferencia)

    def _digerir_caminho(self, caminho, transferencia):
        """
        Alimenta o objeto com as contas do caminho dado, associando a
        transferência dada com esse caminho..

        Argumentos:

        - caminho: uma string no formato explicado abaixo
        - transferencia: o objeto `Transferencia` associado a esse
          caminho

        O caminho devem estar no formato
        `conta:subconta:subconta...`, onde cada subconta é separada
        de sua conta-mãe pelo símbolo definido na variável global
        `SEPARADOR_DE_CONTAS` (nesse exemplo, dois-pontos).
        """

        if not caminho:
            raise ValueError("Caminho vazio: {caminho}!".format(**vars()))

        contas = caminho.split(SEPARADOR_DE_CONTAS)

        pai = self._hierarquia
        for conta in contas:
            if conta not in pai["contas"]:
                pai["contas"][conta] = {
                    "transferencias": [],
                    "contas": {},
                }

            pai = pai["contas"][conta]

        pai["transferencias"].append(transferencia)

    @property
    def dict(self):
        """
        Retorna um `dict` representando a hierarquia de contas com as
        quais o objeto foi alimentado.

        O dicionário retornado é uma estrutura recursiva, onde cada
        chave é o nome de uma conta, e seu item é um outro dicionário
        contendo outra estrutura idência.

        Contas sem filhos são dicionários vazios.

        Exemplo:

        {
            'bens': {
                'grana': {}
            },

            'comida': {
                'organicos': {
                    'dona nilta': {}
                }
            }
        }

        """

        return self._hierarquia
