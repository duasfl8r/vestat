# -*- coding: utf-8 -*-
from fractions import Fraction
from decimal import Decimal
import datetime
import operator
import logging

from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.db.models import Sum, Count
from django.db.utils import DatabaseError
from django.db.models.query_utils import Q
from django.template.defaultfilters import slugify
from durationfield.db.models.fields.duration import DurationField #@UnresolvedImport

from vestat.caixa import NOME_DO_REGISTRO
from vestat.feriados import eh_dia_util, eh_feriado
from vestat.config import config_pages, Link
from vestat.config.models import VestatConfiguration
from vestat.contabil.models import Registro, Transacao, Lancamento
from vestat.contabil import join

logger = logging.getLogger(__name__)

SLUG_CATEGORIA_GORJETA = "10"
"""
Slug do objeto CategoriaDeMovimentacao correspondente ao pagamento de
10% pros funcionários.
"""
SLUG_CATEGORIA_TAXA_CARTAO = "taxas"
"""
Slug do objeto CategoriaDeMovimentacao correspondente ao pagamento de
taxas das bandeiras de cartão.
"""

MESES = [u"janeiro", u"fevereiro", u"março", u"abril",
     u"maio", u"junho", u"julho", u"agosto",
     u"setembro", u"outubro", u"novembro",
     u"dezembro"]

FATOR_CONSIDERADO_10P = Decimal('0.9')
"""
Porcentagem dos 10% considerada no cálculo das parcelas pra casa /
funcionários.

O que não é considerado ness cálculo é usado pra consertar/repor
materiais usados e quebrados do restaurante.
"""


def get_config():
    """
    Retorna o Singleton `VestatConfiguration` configurado no `settings`.

    """

    return VestatConfiguration.objects.get(pk=settings.ID_CONFIG)

def secs_to_time(valor):
    """Transforma segundos em um objeto datetime.time equivalente."""
    if not valor:
        return datetime.time(0)

    segundos = valor % 60 % 60
    minutos = valor // 60 % 60
    horas = valor // 60 // 60
    return datetime.time(int(horas), int(minutos), int(segundos))

def secs_to_time_str(valor):
    segundos = valor % 60 % 60
    minutos = valor // 60 % 60
    horas = valor // 60 // 60
    return "%02d:%02d:%02d" % (horas, minutos, segundos)


class VendasFechadasManager(models.Manager):
    def get_query_set(self):
        return super(VendasFechadasManager, self).get_query_set().filter(fechada=True)

class VendasAbertasManager(models.Manager):
    def get_query_set(self):
        return super(VendasAbertasManager, self).get_query_set().filter(fechada=False)

class Dia(models.Model):
    class Meta:
        ordering = ['data']

    data = models.DateField(unique=True)
    anotacoes = models.TextField(blank=True)
    dia_da_semana = models.IntegerField(editable=False, null=True)

    def save(self, *args, **kwargs):
        self.dia_da_semana = self.data.weekday()
        super(Dia, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/caixa/{0:04d}/{1:02d}/{2:02d}/".format(self.data.year,
                                                         self.data.month,
                                                         self.data.day)

    def __unicode__(self):
        return u"{0}, {1}".format(
            self.data.strftime("%d/%m/%Y").decode("utf-8"),
            self.categoria_semanal(),
        )

    def categoria_semanal(self):
        if eh_feriado(self.data):
            return 'feriado'
        else:
            dias = ['semana', 'semana', 'semana', 'semana', 'sexta', 'sabado', 'domingo']
            return dias[self.data.weekday()]

    @classmethod
    def _anos(cls, objects=None):
        """Retorna um set com todos os anos (como string) de objetos Dia"""

        if objects is None: objects = Dia.objects.all()
        return sorted(set([dia.data.year for dia in objects]))

    @classmethod
    def _meses(cls, ano, objects=None):
        """Retorna um set com todos os meses (como string) de objetos
        Dia do ano `ano`"""

        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(data__year=ano)
        return sorted(set([dia.data.month for dia in objects]))

    @classmethod
    def _dias(cls, ano, mes, objects=None):
        """Retorna todos os dias (como string) de objetos
        Dia do ano `ano` e mês `mes`"""

        if objects is None: objects = Dia.objects.all()
        return objects.filter(data__year=ano, data__month=mes)
    
    @classmethod
    def exportar(cls, format="json"):
        classes = [Dia, Bandeira, Venda, PagamentoComCartao, AjusteDeCaixa,
                   DespesaDeCaixa, MovimentacaoBancaria]
        
        iter_objects = (list(Class.objects.all()) for Class in classes)
        objects = reduce(lambda x,y: x+y, iter_objects)
        return serializers.serialize(format, objects, ensure_ascii=False)
    
    @classmethod
    def importar(cls, file, format="json"):
        for obj in serializers.deserialize(format, file):
            obj.save()

    def vendas_abertas(self):
        return self.venda_set.filter(fechada=False)

    def vendas_fechadas(self):
        return self.venda_set.filter(fechada=True)

    def permanencia_media(self):
        """Retorna a permanência média dos clientes do dia"""

        perm = self.vendas_fechadas().aggregate(Sum('permanencia'))['permanencia__sum']
        if perm:
            return secs_to_time(float(perm) / self.vendas_fechadas().count())

        return 0

    @classmethod
    def permanencia_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        perm = objects.aggregate(Sum('venda__permanencia'))['venda__permanencia__sum']
        return secs_to_time_str(float(perm))
        return 0

    @classmethod
    def permanencia_media_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        perm = objects.aggregate(Sum('venda__permanencia'))['venda__permanencia__sum']
        if perm:
            count = objects.aggregate(Count('venda'))['venda__count']
            return secs_to_time(float(perm) / count)
        return 0

    def caixa(self):
        """Retorna o total ganho em dinheiro no dia."""
        dinheiro = self.vendas_fechadas().aggregate(Sum('pgto_dinheiro'))['pgto_dinheiro__sum']
        cheque = self.vendas_fechadas().aggregate(Sum('pgto_cheque'))['pgto_cheque__sum']
        return sum(filter(None, [dinheiro, cheque]))

    @classmethod
    def caixa_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        dinheiro = objects.aggregate(Sum('venda__pgto_dinheiro'))['venda__pgto_dinheiro__sum']
        cheque = objects.aggregate(Sum('venda__pgto_cheque'))['venda__pgto_cheque__sum']
        return sum(filter(None, [dinheiro, cheque]))
    
    def faturamento_dinheiro(self):
        dinheiro = self.vendas_fechadas().aggregate(Sum('pgto_dinheiro'))['pgto_dinheiro__sum'] 
        return dinheiro if dinheiro else 0
    
    def faturamento_cheque(self):
        cheque = self.vendas_fechadas().aggregate(Sum('pgto_cheque'))['pgto_cheque__sum'] 
        return cheque if cheque else 0
    
    def faturamento_cartao(self):
        return self.faturamento_cartao_credito() + self.faturamento_cartao_debito()
    
    def faturamento_cartao_debito(self):
        cartao = self.vendas_fechadas().filter(pagamentocomcartao__bandeira__categoria='D') \
                                  .aggregate(Sum('pagamentocomcartao__valor')) \
                                    ['pagamentocomcartao__valor__sum'] 
        return cartao if cartao else 0
    
    def faturamento_cartao_credito(self):
        cartao = self.vendas_fechadas().filter(pagamentocomcartao__bandeira__categoria='C') \
                                          .aggregate(Sum('pagamentocomcartao__valor')) \
                                            ['pagamentocomcartao__valor__sum'] 
        return cartao if cartao else 0
    
    def faturamento(self):
        return self.faturamento_dinheiro() + self.faturamento_cartao() + self.faturamento_cheque()

    def faturamento_porcentagem(self):
        """Retorna a porcentagem de despesas em relação ao resultado do dia."""
        return self.faturamento() / self.resultado() * Decimal("100")
    
    @classmethod
    def faturamento_total_dinheiro(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        pgto = objects.aggregate(Sum('venda__pgto_dinheiro'))['venda__pgto_dinheiro__sum']
        return pgto if pgto else 0
    
    @classmethod
    def faturamento_total_cheque(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        pgto = objects.aggregate(Sum('venda__pgto_cheque'))['venda__pgto_cheque__sum']
        return pgto if pgto else 0
    
    @classmethod
    def faturamento_total_cartao_debito(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        pgto = objects.filter(venda__fechada=True, venda__pagamentocomcartao__bandeira__categoria='D') \
                         .aggregate(Sum('venda__pagamentocomcartao__valor')) \
                           ['venda__pagamentocomcartao__valor__sum']
        return pgto if pgto else 0
    
    @classmethod
    def faturamento_total_cartao_credito(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        pgto = objects.filter(venda__fechada=True, venda__pagamentocomcartao__bandeira__categoria='C') \
                         .aggregate(Sum('venda__pagamentocomcartao__valor')) \
                           ['venda__pagamentocomcartao__valor__sum']
        return pgto if pgto else 0
    
    @classmethod
    def faturamento_total_cartao(cls, objects=None):
        return cls.faturamento_total_cartao_credito(objects) + \
               cls.faturamento_total_cartao_debito(objects)

    @classmethod
    def faturamento_total(cls, objects=None):
        return sum([Dia.faturamento_total_dinheiro(objects), Dia.faturamento_total_cheque(objects), Dia.faturamento_total_cartao(objects)])
    
    def despesas_de_caixa(self):
        """Retorna o total de despesas de caixa do dia."""

        despesas_de_caixa = self.despesadecaixa_set.aggregate(Sum('valor'))['valor__sum']
        return despesas_de_caixa if despesas_de_caixa else 0

    @classmethod
    def despesas_de_caixa_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        despesas_de_caixa = objects.aggregate(Sum('despesadecaixa__valor'))['despesadecaixa__valor__sum']
        return despesas_de_caixa if despesas_de_caixa else 0
    
    @classmethod
    def movimentacoes_bancarias_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        movbancarias = objects.aggregate(Sum('movimentacaobancaria__valor'))['movimentacaobancaria__valor__sum']
        return movbancarias if movbancarias else 0
    
    @classmethod
    def debitos_bancarios_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        movbancarias = objects.filter(movimentacaobancaria__valor__lt=0).\
                        aggregate(Sum('movimentacaobancaria__valor'))['movimentacaobancaria__valor__sum']
        return movbancarias if movbancarias else 0
    
    @classmethod
    def creditos_bancarios_total(cls, objects=None):
        if objects is None: objects = Dia.objects.all()
        movbancarias = objects.filter(movimentacaobancaria__valor__gt=0).\
                        aggregate(Sum('movimentacaobancaria__valor'))['movimentacaobancaria__valor__sum']
        return movbancarias if movbancarias else 0
    
    def movimentacoes_bancarias(self):
        movbancarias = self.movimentacaobancaria_set.aggregate(Sum('valor'))['valor__sum']
        return movbancarias if movbancarias else 0
    
    def debitos_bancarios(self):
        movbancarias = self.movimentacaobancaria_set.filter(valor__lt=0).\
                        aggregate(Sum('valor'))['valor__sum']
        return movbancarias if movbancarias else 0
    
    def creditos_bancarios(self):
        movbancarias = self.movimentacaobancaria_set.filter(valor__gt=0).\
                        aggregate(Sum('valor'))['valor__sum']
        return movbancarias if movbancarias else 0
    
    def ajustes_de_caixa(self):
        ajustes = self.ajustedecaixa_set.aggregate(Sum('valor'))['valor__sum']
        return ajustes if ajustes else 0
    
    def despesas(self):
        """Retorna o total de despesas do dia."""

        despesas_de_caixa = self.despesas_de_caixa()
        despesas_bancarias =  self.movimentacaobancaria_set.filter(valor__lt=0).aggregate(Sum('valor'))['valor__sum']

        return sum(filter(None, [despesas_de_caixa, despesas_bancarias]))

    def despesas_porcentagem(self):
        """Retorna a porcentagem de despesas em relação ao resultado do dia."""
        return self.despesas() / self.resultado() * Decimal("100")

    @classmethod
    def despesas_total(cls, objects=None):
        """Retorna o total de despesas de `objects`, ou de
        todos os objetos Dia, se `objects` não for dado"""

        if objects is None: objects = Dia.objects.all()

        despesas_de_caixa = Dia.despesas_de_caixa_total(objects)
        despesas_bancarias =  objects.filter(movimentacaobancaria__valor__lt=0).aggregate(Sum('movimentacaobancaria__valor'))['movimentacaobancaria__valor__sum']

        return sum(filter(None, [despesas_de_caixa, despesas_bancarias]))

    @classmethod
    def gorjeta_total(cls, objects=None):
        """Retorna o total de gorjetas de `objects`, ou de todos os
        objetos Dia, se `objects` não for dado."""

        if objects is None: objects = Dia.objects.all()
        vendas = Venda.objects.filter(dia__in=objects, fechada=True)
        gorjeta = vendas.aggregate(Sum('gorjeta'))['gorjeta__sum']

        if not gorjeta:
            return 0

        return gorjeta * FATOR_CONSIDERADO_10P

    def gorjeta(self):
        """Retorna o total de gorjetas do dia."""

        gorjeta = self.vendas_fechadas().aggregate(Sum('gorjeta'))['gorjeta__sum']
        return gorjeta * Decimal('0.9') if gorjeta else 0

    @classmethod
    def descontos_da_gorjeta(cls, dias=None):
        if dias is None: dias = Dia.objects.all()

        try:
            categoria_gorjeta = CategoriaDeMovimentacao.objects.get(pk=SLUG_CATEGORIA_GORJETA)
        except CategoriaDeMovimentacao.DoesNotExist:
            return Decimal("0")

        despesas_de_caixa = DespesaDeCaixa.objects.filter(categoria=categoria_gorjeta, dia__in=dias)
        pagamento_com_gorjetas_caixa = despesas_de_caixa.aggregate(Sum('valor'))['valor__sum']
        if not pagamento_com_gorjetas_caixa:
            pagamento_com_gorjetas_caixa = 0

        despesas_banco = MovimentacaoBancaria.objects.filter(categoria=categoria_gorjeta, dia__in=dias)
        pagamento_com_gorjetas_banco = despesas_banco.aggregate(Sum('valor'))['valor__sum']
        if not pagamento_com_gorjetas_banco:
            pagamento_com_gorjetas_banco = 0

        return pagamento_com_gorjetas_caixa + pagamento_com_gorjetas_banco

    def dez_porcento_a_pagar(self):
        """
        Retorna o total de 10% a pagar -- o total de dívidas de 10% aos
        funcionários menos o total já pago a eles -- até certa o dia atual.

        """

        config = get_config()

        dias = Dia.objects.filter(data__lte=self.data)
        pagamento_com_gorjetas = self.descontos_da_gorjeta(dias)

        registro_10p = Registro.objects.get(nome=NOME_DO_REGISTRO)

        total_dividas_10p = registro_10p.balanco(
            join("dividas", "contas a pagar", "10%"),
            ateh=self.data,
        )

        return pagamento_com_gorjetas - total_dividas_10p
    
    @classmethod
    def ajuste_total(cls, objects=None):
        """Retorna o total de ajustes do dia."""
        
        if objects is None: objects = Dia.objects.all()
        ajuste = objects.aggregate(Sum('ajustedecaixa__valor'))['ajustedecaixa__valor__sum']
        return ajuste if ajuste else 0
    
    def ajuste(self):
        """Retorna o total de ajustes do dia."""
        
        ajuste = self.ajustedecaixa_set.aggregate(Sum('valor'))['valor__sum']
        return ajuste if ajuste else 0

    @classmethod
    def resultado_total(cls, objects=None):
        """Retorna o resultado (lucro ou prejuízo) de `objects`, ou de todos os
        objetos Dia, se `objects` não for dado."""

        if objects is None: objects = Dia.objects.all()
        resultado = cls.faturamento_total(objects) + cls.despesas_total(objects)
        return resultado if resultado else 0

    def resultado(self):
        """Retorna o resultado (lucro ou prejuízo) do dia"""

        resultado = self.faturamento() + self.despesas()
        return resultado if resultado else 0

    def caixa_de_hoje(self):
        """Retorna o total de dinheiro no caixa no dia"""
        dias = Dia.dias_entre(None, self.data)
        return Dia.faturamento_total_dinheiro(dias) + \
               Dia.faturamento_total_cheque(dias) + \
               Dia.despesas_de_caixa_total(dias) + \
               Dia.ajuste_total(dias)
    
    def captacao_por_pessoa(self):
        if self.vendas_fechadas().count():
            return self.faturamento() / self.num_pessoas()
        return 0

    @classmethod
    def captacao_por_pessoa_total(cls, objects=None):
        num_pessoas = Dia.num_pessoas_total(objects)
        if num_pessoas:
            return cls.faturamento_total(objects) / num_pessoas
        return 0

    @classmethod
    def num_pessoas_total(cls, objects=None):
        """Retorna o número de pessoas de `objects`, ou de todos os
        objetos Dia, se `objects` não for dado."""

        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        num_pessoas = objects.aggregate(Sum('venda__num_pessoas'))['venda__num_pessoas__sum']
        return num_pessoas if num_pessoas else 0

    def num_pessoas(self):
        """Retorna o num_pessoas (lucro ou prejuízo) do dia"""

        num_pessoas = self.vendas_fechadas().aggregate(Sum('num_pessoas'))['num_pessoas__sum']
        return num_pessoas if num_pessoas else 0

    @classmethod
    def vendas_total(cls, objects=None):
        """Retorna o número de vendas de `objects`, ou de todos os
        objetos Dia, se `objects` não for dado."""

        if objects is None: objects = Dia.objects.all()
        objects = objects.filter(venda__fechada=True)
        vendas = objects.aggregate(Count('venda'))['venda__count']
        return vendas if vendas else 0

    def vendas(self):
        """Retorna o número de vendas do dia"""

        return self.vendas_fechadas().count()

    @classmethod
    def fim_do_ano(cls, ano):
        um_dia = datetime.timedelta(1)
        return datetime.date(ano + 1, 1, 1) - um_dia
    
    @classmethod
    def fim_do_mes(cls, ano, mes):
        prox_mes, prox_ano = (1, ano + 1) if mes == 12 else (mes + 1, ano)
        um_dia = datetime.timedelta(1)
        return datetime.date(prox_ano, prox_mes, 1) - um_dia
    
    @classmethod
    def dias_entre(cls, d1=None, d2=None):
        """Retorna um QuerySet de dias entre d1 e d2, inclusive."""
        dias = cls.objects.all()
        dias = dias.filter(data__gte=d1) if d1 else dias
        dias = dias.filter(data__lte=d2) if d2 else dias
        return dias
    
    @classmethod
    def listar_dias(cls, de=None, ateh=None, dias_da_semana=range(0, 8)):
        dias = cls.dias_entre(de, ateh).order_by("-data")

        dados = {
                   "faturamento_total": {
                                            "total": cls.faturamento_total(dias),
                                            "dinheiro": cls.faturamento_total_dinheiro(dias),
                                            "cheque": cls.faturamento_total_cheque(dias),
                                            "cartao_debito": cls.faturamento_total_cartao_debito(dias),
                                            "cartao_credito": cls.faturamento_total_cartao_credito(dias),
                                        },
                  "vendas_total": cls.vendas_total(dias),
                  "num_pessoas_total": cls.num_pessoas_total(dias),
                  "permanencia_media_total": cls.permanencia_media_total(dias),
                  "captacao_por_pessoa_total": cls.captacao_por_pessoa_total(dias),
                  "gorjeta_total": cls.gorjeta_total(dias),
                  "despesas_de_caixa_total": cls.despesas_de_caixa_total(dias),
                  "movimentacoes_bancarias_total": cls.movimentacoes_bancarias_total(dias),
                  "resultado_total": cls.faturamento_total(dias) + cls.despesas_total(dias),
                  "dias": dias,
                }
    
        return dados
    
    @classmethod
    def estruturar_dias(cls, dias=None):
        if dias == None: dias = cls.objects.all()
        dias = dias.order_by("-data")
    
        anos = {}
        for ano in sorted(cls._anos()):
            dias_do_ano = cls.objects.filter(data__year=ano)
            dias_ate_ano = cls.objects.filter(data__lte=cls.fim_do_ano(ano))
    
            meses = {}
            for mes in cls._meses(ano, dias):
                dias_do_mes = cls.objects.filter(data__year=ano, data__month=mes)
                dias_ate_mes = cls.objects.filter(data__lte=cls.fim_do_mes(ano, mes))
    
                meses[mes] = { "nome": MESES[mes-1],
                               "vendas": cls.vendas_total(dias_do_mes),
                               "num_pessoas": cls.num_pessoas_total(dias_do_mes),
                               "permanencia_media": cls.permanencia_media_total(dias_do_mes),
                               "captacao_por_pessoa": cls.captacao_por_pessoa_total(dias_do_mes),
                               "faturamento": cls.faturamento_total(dias_do_mes),
                               "faturamento_acumulado": cls.faturamento_total(dias_ate_mes),
                               "despesas_de_caixa": cls.despesas_de_caixa_total(dias_do_mes),
                               "despesas_de_caixa_acumulado": cls.despesas_de_caixa_total(dias_ate_mes),
                               "movimentacoes_bancarias": cls.movimentacoes_bancarias_total(dias_do_mes),
                               "movimentacoes_bancarias_acumulado": cls.movimentacoes_bancarias_total(dias_ate_mes),
                               "gorjeta": cls.gorjeta_total(dias_do_mes),
                               "gorjeta_acumulado": cls.gorjeta_total(dias_ate_mes),
                               "despesas": cls.despesas_total(dias_do_mes),
                               "despesas_acumulado": cls.despesas_total(dias_ate_mes),
                               "resultado": cls.faturamento_total(dias_do_mes) + cls.despesas_total(dias_do_mes),
                               "resultado_acumulado": cls.faturamento_total(dias_ate_mes) + cls.despesas_total(dias_ate_mes),
                               "dias": dias_do_mes }
    
            anos[ano] = { "nome": ano,
                          "num_pessoas": cls.num_pessoas_total(dias_do_ano),
                          "vendas": cls.vendas_total(dias_do_ano),
                          "permanencia_media": cls.permanencia_media_total(dias_do_ano),
                          "captacao_por_pessoa": cls.captacao_por_pessoa_total(dias_do_ano),
                          "faturamento": cls.faturamento_total(dias_do_ano),
                          "faturamento_acumulado": cls.faturamento_total(dias_ate_ano),
                          "despesas_de_caixa": cls.despesas_de_caixa_total(dias_do_ano),
                          "despesas_de_caixa_acumulado": cls.despesas_de_caixa_total(dias_ate_ano),
                          "movimentacoes_bancarias": cls.movimentacoes_bancarias_total(dias_do_ano),
                          "movimentacoes_bancarias_acumulado": cls.movimentacoes_bancarias_total(dias_ate_ano),
                          "gorjeta": cls.gorjeta_total(dias_do_ano),
                          "gorjeta_acumulado": cls.gorjeta_total(dias_ate_ano),
                          "despesas": cls.despesas_total(dias_do_ano),
                          "despesas_acumulado": cls.despesas_total(dias_ate_ano),
                          "resultado": cls.faturamento_total(dias_do_ano) + cls.despesas_total(dias_do_ano),
                          "resultado_acumulado": cls.faturamento_total(dias_ate_ano) + cls.despesas_total(dias_ate_ano),
                          "meses": meses }
    
        return anos


class Bandeira(models.Model):
    CONTAGEM_DE_DIAS_CHOICES = (
        ('U', 'Dias úteis'),
        ('C', 'Dias corridos')
    )

    CATEGORIA_CHOICES = (
        ('C', 'Crédito'),
        ('D', 'Débito')
    )

    ativa = models.BooleanField("Ativa?", help_text="Bandeiras ativas podem ser escolhidas pra um pagamento.", default=True)
    nome = models.CharField(max_length=20)
    taxa = models.DecimalField("Taxa coletada pela bandeira", max_digits=6, decimal_places=5)
    prazo_de_deposito = models.IntegerField("Dias até o depósito")
    contagem_de_dias = models.CharField(max_length=1, choices=CONTAGEM_DE_DIAS_CHOICES)
    categoria = models.CharField(max_length=1, choices=CATEGORIA_CHOICES)

    def __unicode__(self):
        return self.nome


class PagamentoComCartao(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    venda = models.ForeignKey('Venda', editable=False)
    bandeira = models.ForeignKey(Bandeira)

    data_do_deposito = models.DateField("Data do depósito do pagamento", editable=False, null=True)
    # Data do depósito do pagamento feito pelo cliente na conta do restaurante.
    #
    # Embora ter essa data como um campo viole o princípio DRY (Don't Repeat Yourself),
    # isso torna muito mais fácil a montagem do calendário com a
    # previsão dos dias de pagamento.

    @property
    def taxa(self):
        """Retorna a taxa cobrada pela bandeira do cartão por esse pagamento."""
        return self.valor * self.bandeira.taxa

    def get_absolute_url(self):
        return self.venda.get_absolute_url() + "cartao/{0}/".format(self.id)

    def _data_do_deposito(self):
        data_da_venda = self.venda.dia.data
        um_dia = datetime.timedelta(1)
        intervalo = datetime.timedelta(0)
        faltam_dias = self.bandeira.prazo_de_deposito
        soh_dias_uteis = self.bandeira.contagem_de_dias == "U"

        while faltam_dias:
            intervalo += um_dia
            data_teste = data_da_venda + intervalo

            if soh_dias_uteis:
                if eh_dia_util(data_teste):
                    faltam_dias -= 1
            else:
                faltam_dias -= 1

        return data_da_venda + intervalo

    def save(self, *args, **kwargs):
        super(PagamentoComCartao, self).save(*args, **kwargs)

        categoria_taxas = CategoriaDeMovimentacao.objects.get(slug=SLUG_CATEGORIA_TAXA_CARTAO)

        self.venda.dia.movimentacaobancaria_set.create(valor=-self.taxa,
            categoria=categoria_taxas, descricao=self.bandeira.nome,
            pgto_cartao=self)

        self.venda.dia.save()

        self.data_do_deposito = self._data_do_deposito()
        super(PagamentoComCartao, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"R$ %.2f, %s" % (self.valor, self.bandeira)


class Venda(models.Model):
    CATEGORIA_CHOICES = (
        ('L', 'Local'),
        ('T', 'Turista'),
        ('V', 'Veraneio'),
    )

    CIDADE_CHOICES = map(lambda x: (x, x), sorted((
        u'Cachoeiras de Macacu', u'Rio de Janeiro', u'Nova Friburgo', u'Macaé',
        u'Rio das Ostras', u'Niterói', u'São Gonçalo', u'Cabo Frio', u'Búzios',
    )))

    # len(choice) <= 20
    POUSADA_CHOICES = (
        ('São Pedro da Serra', map(lambda x: (x, x), sorted((
                u'Amarylis', u'Bocaina', u'Bom Bocado', u'Canteiros',
                u'Canto da Mata', u'Canto dos Ventos', u'Canto Nosso', u'Degustarte',
                u'Estrela da Manhã', u'Flor da Serra', u'Galo da Serra', u'La Golondrina',
                u'Lírio do Campo', u'Nagual', u'Pousada dos Anjos', u'Rec dos Eucaliptos',
                u'São Saruê', u'Solar do Passaredo', u'Vila do Céu',
        )))),
        ('Lumiar', map(lambda x: (x, x), sorted((
                u'Chalés Lumiar', u'Rancho Eldorado', u'Aliá', u'Arte-de-Viver',
                u'Brilho do Sol', u'Caminho das Candeias', u'Eco das Folhas', u'Klein',
                u'Jardim Real', u'Luar da Serra', u'Paraíso do Rio', u'Flor das Águas',
                u'Panorama', u'Parador Lumiar', u'Alê Friburgo Hostel', u'Cabanas Lumiar',
                u'Camping Artur', u'Conde Redondo', u'Pedra Riscada', u'Novo Espaço Lumiar',
                u'Canopy Brasil', u'Cascata', u'Encanto do Recanto', u'Encontro dos Rios',
                u'Estação Lumiar', u'Fonte Viva', u'Nova Estação', u'Recanto das Águas',
                u'Recanto das Pedras', u'Pierrô', u'Tiê', u'Toca da Onça',

        )))),
    )

    dia = models.ForeignKey('Dia', editable=False)
    mesa = models.CharField(max_length=10)
    hora_entrada = models.TimeField('hora de entrada')
    hora_saida = models.TimeField('hora de saída', null=True)
    permanencia = models.IntegerField('permanência', editable=False, null=True)
    num_pessoas = models.IntegerField('pessoas', null=True)
    conta = models.DecimalField('total da conta', max_digits=10, decimal_places=2, default=0)
    gorjeta = models.DecimalField('10%', max_digits=10, decimal_places=2, default=0)
    categoria = models.CharField(max_length=1, choices=CATEGORIA_CHOICES)
    cidade_de_origem = models.CharField('cidade', max_length=20, blank=True, choices=CIDADE_CHOICES)
    pousada_que_indicou = models.CharField('pousada', max_length=20, blank=True, choices=POUSADA_CHOICES)
    pgto_dinheiro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pgto_cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fechada = models.BooleanField(editable=False, default=False);

    transacao_10p = models.ForeignKey(Transacao, null=True, editable=False, related_name="+")

    objects = models.Manager()
    abertas = VendasAbertasManager()
    fechadas = VendasFechadasManager()

    def __unicode__(self):
        return u"%s - %s, %d %s, R$ %.2f, %s" % \
            (self.hora_entrada.strftime("%H:%M"),
             self.hora_saida.strftime("%H:%M"),
             self.num_pessoas, (self.num_pessoas == 1 and "pessoa" or "pessoas"),
             self.conta,
             dict(self.CATEGORIA_CHOICES)[self.categoria])

    def get_absolute_url(self):
        return self.dia.get_absolute_url() + "venda/{0}/".format(self.id)
    
    def pgto_cartao(self):
        if self.pagamentocomcartao_set.count():
            return self.pagamentocomcartao_set.aggregate(Sum("valor"))['valor__sum']
        else:
            return 0

    def permanencia_time(self):
        """Retorna a permanência como um objeto time"""
        return secs_to_time(self.permanencia)

    def calcular_permanencia(self, t1, t2):
        """ Retorna a diferença de tempo entre t1 e t2, em segundos."""
        h1 = t1.hour + t1.minute / 60.0
        h2 = t2.hour + t2.minute / 60.0
        if (t1 > t2): # se começa num dia e termina no outro
            h2 += 24
        return int(3600 * (h2 - h1))

    def abrir(self):
        """
        Torna a venda aberta -- o cliente ainda está consumindo.
        """

        if not self.fechada:
            return

        if self.transacao_10p:
            self.transacao_10p.delete()

        self.fechada = False
        self.save()

    def fechar(self):
        """
        Torna a venda fechada -- o cliente já pagou a conta.

        Cria/sobrescreve a transação de 10% referente à venda.

        """

        if self.fechada:
            return

        if self.transacao_10p:
            self.transacao_10p.delete()

        if self.gorjeta:
            registro_10p = Registro.objects.get(nome=NOME_DO_REGISTRO)

            self.transacao_10p = Transacao(
                registro=registro_10p,
                data=self.dia.data,
                descricao="10% a pagar do dia {0}".format(self.dia.data)
            )

            self.transacao_10p.save()

            config = get_config()

            a_pagar = Decimal(
                float(
                    Fraction.from_decimal(self.gorjeta) \
                     * Fraction(9, 10) \
                     * config.fracao_10p_funcionarios
                 )
            )

            self.transacao_10p.lancamentos.create(
                valor=a_pagar * -1,
                conta=join("entrada", "vendas", "10% funcionarios"),
            )

            self.transacao_10p.lancamentos.create(
                valor=a_pagar,
                conta=join("bens", "caixa"),
            )

            self.transacao_10p.lancamentos.create(
                valor=a_pagar,
                conta=join("gastos", "funcionarios", "10%"),
            )

            self.transacao_10p.lancamentos.create(
                valor=a_pagar * -1,
                conta=join("dividas", "contas a pagar", "10%"),
            )


        self.fechada = True
        self.save()

    def delete(self, *args, **kwargs):
        if self.transacao_10p:
            self.transacao_10p.delete()
        super(Venda, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.hora_saida is not None:
            self.permanencia = self.calcular_permanencia(self.hora_entrada, self.hora_saida)
        super(Venda, self).save(*args, **kwargs)

    def total_de_pagamentos(self):
        """Retorna a soma dos pagamentos (dinheiro, cheque, cartão)
           feitos nessa compra."""

        total = self.pgto_dinheiro and self.pgto_dinheiro or Decimal('0')
        total += self.pgto_cheque and self.pgto_cheque or Decimal('0')
        for pgto_cartao in self.pagamentocomcartao_set.all():
            total += pgto_cartao.valor
        return total


class AjusteDeCaixa(models.Model):
    class Meta:
        verbose_name = "Ajuste de caixa"
        verbose_name_plural = "Ajustes de caixa"
        
    dia = models.ForeignKey('Dia', editable=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=150, blank=True)

    def __unicode__(self):
        return u"R$ %.2f - %s" % (self.valor, self.descricao)

    def get_absolute_url(self):
        return self.dia.get_absolute_url() + "ajuste/{0}/".format(self.id)


class CategoriaDeMovimentacao(models.Model):
    """
    Categoria aninhável, usada nas classes `DespesaDeCaixa` e
    `MovimentacaoBancaria`.

    Uma categoria `A` é *filha* de uma categoria `B` se ``B.mae == A``.
    """

    class Meta:
        verbose_name = "Categoria de movimentação"
        verbose_name_plural = "Categorias de movimentação"

    nome = models.CharField(max_length=200)
    """
    Nome da categoria (e.g. "Tarifas bancárias")
    """
    slug = models.SlugField()
    """
    Nome da categoria, usando somente letras, números e hífens (e.g. "tarifas-bancarias").
    """
    mae = models.ForeignKey("self", blank=True, null=True, related_name="filhas")
    """
    Nome da categoria-mãe; se não for especificado, a categoria é de nível primário.
    """

    SEPARADOR = " > "
    """
    String usada pra separar categorias no nome completo de uma categoria
    (e.g. "Fornecedor > Bebidas").
    """

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        """
        Gera slug automático caso não seja especificado, e salva o objeto no banco de dados.
        """

        if not self.slug:
            logger.debug(u"Gerando slug automático pra categoria '{0}'...".format(self.nome))
            self.slug = slugify(self.nome)

        super(CategoriaDeMovimentacao, self).save(*args, **kwargs)

    @property
    def ascendentes(self):
        """
        Retorna lista das categorias ascendentes de uma categoria.

        Por exemplo:

        >>> categoria
        <CategoriaDeMovimentacao: Vinhos>
        >>> categoria.nome_completo
        'Fornecedor > Bebidas > Vinhos'
        >>> categoria.ascendentes
        [<CategoriaDeMovimentacao: Fornecedor>, <CategoriaDeMovimentacao: Bebidas>]

        """
        def ascendentes_(categoria):
            yield categoria
            if categoria.mae:
                ascendentes_(categoria.mae)

        return list(ascendentes_(self.mae)) if self.mae else []

    @property
    def nome_completo(self):
        """
        Retorna o nome da categoria e de todas as categorias
        ascendentes, na ordem da mais alta pra própria categoria,
        separados por `CategoriaDeMovimentacao.SEPARADOR`.

        Por exemplo:

        >>> categoria
        <CategoriaDeMovimentacao: Vinhos>
        >>> categoria.mae
        <CategoriaDeMovimentacao: Bebidas>
        >>> categoria.mae.mae
        <CategoriaDeMovimentacao: Fornecedores>
        >>> categoria.mae.mae.mae is None
        True
        >>> categoria.nome_completo
        'Fornecedor > Bebidas > Vinhos'
        """
        return self.SEPARADOR.join(unicode(a) for a in self.ascendentes + [self])


class DespesaDeCaixa(models.Model):
    class Meta:
        verbose_name = "Despesa de caixa"
        verbose_name_plural = "Despesas de caixa"

    dia = models.ForeignKey('Dia', editable=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey('CategoriaDeMovimentacao', null=True, blank=True)
    descricao = models.CharField('Descrição', max_length=150, blank=True)

    def __unicode__(self):
        return u"R$ %.2f - %s" % (self.valor, self.categoria)

    def get_absolute_url(self):
        return self.dia.get_absolute_url() + "despesa/{0}/".format(self.id)

    def save(self, *args, **kwargs):
        if self.valor > 0: self.valor *= -1
        super(DespesaDeCaixa, self).save(*args, **kwargs)


class MovimentacaoBancaria(models.Model):
    class Meta:
        verbose_name = "Movimentação bancária"
        verbose_name_plural = "Movimentações bancárias"

    dia = models.ForeignKey('Dia', editable=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField('Descrição', max_length=150, blank=True)
    categoria = models.ForeignKey('CategoriaDeMovimentacao', null=True, blank=True)
    pgto_cartao = models.ForeignKey('PagamentoComCartao', null=True, editable=False)

    def __unicode__(self):
        return u"R$ %.2f - %s" % (self.valor, self.categoria)

    def get_absolute_url(self):
        return self.dia.get_absolute_url() + "movbancaria/{0}/".format(self.id)

config_pages["vestat"].add(
    Link(
        "bandeiras",
        "Bandeiras de cartão de crédito/débito",
        reverse_lazy("admin:caixa_bandeira_changelist"),
        "Adicionar/remover/editar"
    ),
)

config_pages["vestat"].add(
    Link(
        "categorias",
        "Categorias de despesas de caixa e movimentações bancárias",
        reverse_lazy("admin:caixa_categoriademovimentacao_changelist"),
        "Adicionar/remover/editar"
    ),
    "Caixa",
)

config_pages["vestat"].add(
    Link(
        "despesadecaixa",
        "Despesas de caixa",
        reverse_lazy("admin:caixa_despesadecaixa_changelist"),
        "Adicionar/remover/editar"
    ),
    "Caixa",
)

config_pages["vestat"].add(
    Link(
        "movbancaria",
        "Movimentações bancárias",
        reverse_lazy("admin:caixa_movimentacaobancaria_changelist"),
        "Adicionar/remover/editar"
    ),
    "Caixa",
)
