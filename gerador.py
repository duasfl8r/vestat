# -*- encoding: utf8 -*-

import datetime
from decimal import Decimal
import random as r

import settings
from django.core.management import setup_environ
setup_environ(settings)

from django.db.utils import IntegrityError

from caixa.models import *

import cProfile

def datas(inicio, fim):
    """Gerador de datas.

    Gera todos os datas entre os objetos datetime.date `inicio`
    (inclusive) e `fim` (exclusive)."""

    UM_DIA = datetime.timedelta(1)
    contador = 0
    while inicio + (contador * UM_DIA) < fim:
        yield inicio + (contador * UM_DIA)
        contador += 1

def gerar_venda(dia):
    """Gera uma venda aleatoriamente."""

    def converter_hora(h):
        """Converte uma hora do formato decimal pra um objeto datetime.time.

        Exemplo: 2.5 -> datetime.time(2, 30)."""

        return datetime.time(int(h), int((h % 1) * 60))

    mesa = str(r.choice(range(1, 10)))
    hora_entrada_dec = r.gauss(22, 1)
    hora_entrada = converter_hora(hora_entrada_dec % 24)
    hora_saida_dec = hora_entrada_dec + r.gauss(1, 1)
    while hora_saida_dec <= hora_entrada_dec:
        hora_saida_dec = hora_entrada_dec + r.gauss(1, 1)
    hora_saida = converter_hora(hora_saida_dec % 24)
    num_pessoas = r.choice([2] * 8 + range(1, 16))
    categoria_venda = r.choice(['T'] * 20 + ['L'] * 5 + ['V'])
    if categoria_venda in ['T', 'V']:
        cidade = r.choice(Venda.CIDADE_CHOICES)
        pousada = r.choice(Venda.POUSADA_CHOICES)
    else:
        cidade = pousada = ""
    conta = Decimal(str(r.triangular(10, 400, 70)))
    if r.random() < 0.05:
        gorjeta = Decimal('0')
    else:
        gorjeta = Decimal(str(r.gauss(float(conta) * 0.1, float(conta) * 0.01)))
    choices = ['CX'] * 10 + ['CH'] + ['CR'] * 15
    pgtos = [r.choice(choices) for i in range(num_pessoas)]
    divisao = conta / len(pgtos)
    pgto_dinheiro = Decimal('0')
    pgto_cheque = Decimal('0')
    pgtos_cartao = []
    for pgto in pgtos:
        if pgto == 'CX':
            pgto_dinheiro += divisao
        elif pgto == 'CH':
            pgto_cheque += divisao
        else:
            bandeira = r.choice(Bandeira.objects.all())
            valor = divisao
            categoria_cartao = r.choice(['C', 'D'])
            pgtos_cartao.append(PagamentoComCartao(bandeira=bandeira,
                valor=valor, categoria=categoria_cartao))
    venda = Venda(dia=dia, mesa=mesa, hora_entrada=hora_entrada,
                  hora_saida=hora_saida, num_pessoas=num_pessoas,
                  categoria=categoria_venda, cidade_de_origem=cidade,
                  pousada_que_indicou=pousada, conta=conta,
                  gorjeta=gorjeta, pgto_dinheiro=pgto_dinheiro,
                  pgto_cheque=pgto_cheque, fechada=True)
    venda.save()
    venda.pagamentocomcartao_set.add(*pgtos_cartao)

def gerar_movbancaria(dia):
    valor = Decimal(str(r.triangular(10, 500, 100))) * r.choice([1, -1])
    descricao = "Gerado aleatoriamente"
    MovimentacaoBancaria(dia=dia, valor=valor, descricao=descricao).save()

def gerar_despesa(dia):
    valor = Decimal(str(r.triangular(10, 500, 100)))
    categoria = r.choice(['F'] * 10 + ['P'] * 6 + ['R'])
    descricao = "Gerado aleatoriamente"
    DespesaDeCaixa(dia=dia, valor=valor, categoria=categoria,
        descricao=descricao).save()

if __name__ == '__main__':
    DATA_INICIO = datetime.date(2011, 01, 01)
    DATA_FIM = datetime.date(2011, 03, 31)
    for data in datas(DATA_INICIO, DATA_FIM):
        print "# Dia:", data
        try:
            dia = Dia(data=data, feriado=(r.random() < 0.05))
            dia.save()
        except IntegrityError:
            dia = Dia.objects.get(data=data)
        for i in range(int(r.triangular(2, 16, 6))):
            gerar_venda(dia)
        for i in range(int(r.triangular(0, 15, 7))):
            gerar_movbancaria(dia)
        for i in range(int(r.triangular(0, 5, 2))):
            gerar_despesa(dia)
