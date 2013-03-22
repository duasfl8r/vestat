# -*- encoding: utf-8 -*-
import codecs
import json

last_bandeira_pk = 0

def converter_cartoes(filename):
    bandeira_antiga_pra_nova = {}

    def handle_bandeira(bandeira):
        global last_bandeira_pk

        bandeira_nova_credito = {
            u"pk": last_bandeira_pk + 1,
            u"model": u"caixa.bandeira",

            u"fields": {
                u"ativa": True,
                u"nome": bandeira["fields"]["nome"] + u" Crédito",
                u"taxa": bandeira["fields"]["taxa_credito"],
                u"prazo_de_deposito": 31,
                u"contagem_de_dias": "C",
                u"categoria": "C",
            }
        }

        bandeira_nova_debito = {
            u"pk": last_bandeira_pk + 2,
            u"model": u"caixa.bandeira",

            u"fields": {
                u"ativa": True,
                u"nome": bandeira["fields"]["nome"] + u" Débito",
                u"taxa": bandeira["fields"]["taxa_debito"],
                u"prazo_de_deposito": 2,
                u"contagem_de_dias": "U",
                u"categoria": "C",
            },
        }

        last_bandeira_pk += 2

        bandeira_antiga_pra_nova[bandeira["pk"]] = {
            "C": bandeira_nova_credito["pk"],
            "D": bandeira_nova_debito["pk"],
        }

        return bandeira_nova_credito, bandeira_nova_debito

    def handle_pagamentocomcartao(pagamentocomcartao):
        bandeira_antiga = pagamentocomcartao["fields"]["bandeira"]
        categoria = pagamentocomcartao["fields"]["categoria"]

        bandeira_nova = bandeira_antiga_pra_nova[bandeira_antiga][categoria]

        pagamentocomcartao_novo = {
            u"pk": pagamentocomcartao["pk"],
            u"model": u"caixa.pagamentocomcartao",

            u"fields": {
                u"venda": pagamentocomcartao["fields"]["venda"],
                u"bandeira": bandeira_nova,
                u"valor": pagamentocomcartao["fields"]["valor"],
            },
        }

        return [pagamentocomcartao_novo]


    print("Carregando arquivo de dump...")

    dump = json.load(codecs.open(filename, encoding="utf-8"))

    model_and_function = (
        ("caixa.bandeira", handle_bandeira),
        ("caixa.pagamentocomcartao", handle_pagamentocomcartao)
    )

    not_to_be_converted = [e for e in dump if e['model'] not in [m[0] for m in model_and_function]]

    print("Convertendo modelos no formato antigo...")

    result = []

    for model, func in model_and_function:
        for elem in [e for e in dump if e['model'] == model]:
            result.extend(func(elem))

    result.extend(not_to_be_converted)

    print("Transformando resultado em JSON")

    return json.dumps(result)
