# -*- encoding: utf-8 -*-
"""
Funções pra converter o dump (saída do `manage.py dumpdata`) da versão
1.2.1 pra 1.2.2.

Converte as categorias antigas (ChoiceField's) pras categorias novas
(objetos `caixa.CategoriaDeMovimentacao`).

Converte objetos `caixa.DespesaDeCaixa` e `caixa.MovimentacaoBancaria`
pra usar as novas categorias, de acordo com uma tabela de conversão
fornecida pelo cliente.

Remove o antigo método de declaração de feriados (através de um atributo
de `caixa.Dia`)

Converte objetos `caixa.Bandeira` para o novo modelo, com informações de
contagem de dias pra depósito em conta.

Converte objetos `caixa.PagamentoComCartao` para usar o novo modelo de
bandeiras.

"""

import codecs
import json

from vestat.caixa.models import CategoriaDeMovimentacao as Cat

BANDEIRAS__TABELA = {}
BANDEIRAS__LAST_PK = 0
CATEGORIAS__NOVAS = {}

def converter(filename):
    """
    Abre o arquivo de dump JSON fornecido, faz as conversões, e retorna
    uma string com um novo arquivo de dump JSON, apropriado pra ser
    importado pela nova versão do Vestat.
    """

    CATEGORIAS__NOVAS["aluguel"] = Cat(nome=u"Aluguel")
    CATEGORIAS__NOVAS["contador"] = Cat(nome=u"Contador")
    CATEGORIAS__NOVAS["energia"] = Cat(nome=u"Energia")
    CATEGORIAS__NOVAS["fornecedor"] = FORNECEDOR = Cat(nome=u"Fornecedor")
    CATEGORIAS__NOVAS["impostos"] = Cat(nome=u"Impostos")
    CATEGORIAS__NOVAS["manutencao"] = Cat(nome=u"Manutenção Predial")
    CATEGORIAS__NOVAS["marketing"] = Cat(nome=u"Marketing")
    CATEGORIAS__NOVAS["pessoal"] = PESSOAL = Cat(nome=u"Pessoal")
    CATEGORIAS__NOVAS["servico"] = Cat(nome=u"Prestação de serviço")
    CATEGORIAS__NOVAS["retirada"] = Cat(nome=u"Retirada")
    CATEGORIAS__NOVAS["tarifas_bancarias"] = Cat(nome=u"Tarifas bancárias")
    CATEGORIAS__NOVAS["taxas"] = Cat(nome=u"Taxas")
    CATEGORIAS__NOVAS["telefone"] = Cat(nome=u"Telefone")

    for c in CATEGORIAS__NOVAS.values(): c.save()

    CATEGORIAS__NOVAS["fornecedor__alemaes"] = Cat(nome=u"Alemães", mae=FORNECEDOR)
    CATEGORIAS__NOVAS["fornecedor__acougue"] = Cat(nome=u"Açougue", mae=FORNECEDOR)
    CATEGORIAS__NOVAS["fornecedor__mercearia"] = Cat(nome=u"Mercearia", mae=FORNECEDOR)
    CATEGORIAS__NOVAS["fornecedor__bebidas"] = Cat(nome=u"Bebidas", mae=FORNECEDOR)
    CATEGORIAS__NOVAS["fornecedor__nao_vendavel"] = Cat(nome=u"Não-vendável", mae=FORNECEDOR)
    CATEGORIAS__NOVAS["pessoal__10p"] = Cat(nome=u"10%", mae=PESSOAL)
    CATEGORIAS__NOVAS["pessoal__extra"] = Cat(nome=u"Extra", mae=PESSOAL)
    CATEGORIAS__NOVAS["pessoal__salario"] = Cat(nome=u"Salário", mae=PESSOAL)

    for c in CATEGORIAS__NOVAS.values(): c.save()

    CATEGORIAS__TABELA = {
        'A': 'aluguel',
        'C': 'contador',
        'E': 'energia',
        'F': 'fornecedor',
        'L': 'fornecedor__alemaes',
        '1': 'fornecedor__acougue',
        'Y': 'fornecedor__mercearia',
        'V': 'fornecedor__bebidas',
        'I': 'impostos',
        'Q': 'manutencao',
        'M': 'marketing',
        'O': None,
        'G': 'pessoal__10p',
        'X': 'pessoal__extra',
        'P': 'pessoal__salario',
        'S': 'servico',
        'U': 'fornecedor__nao_vendavel',
        'R': 'retirada',
        'B': 'tarifas_bancarias',
        'T': 'taxas',
        'N': 'telefone',
    }

    def id_nova_categoria(obj):
        old_code = obj["fields"]["categoria"]
        new_key = CATEGORIAS__TABELA[old_code]
        if new_key is None:
            return None
        else:
            return CATEGORIAS__NOVAS[new_key].id


    def handle_despesadecaixa(despesa):
        return [{
            u"pk": despesa["pk"],
            u"model": u"caixa.despesadecaixa",

            u"fields": {
                u"descricao": despesa["fields"]["descricao"],
                u"dia": despesa["fields"]["dia"],
                u"valor": despesa["fields"]["valor"],
                u"categoria": id_nova_categoria(despesa),
            }
        }]

    def handle_movimentacaobancaria(movbancaria):
        return [{
            u"pk": movbancaria["pk"],
            u"model": u"caixa.movimentacaobancaria",

            u"fields": {
                u"descricao": movbancaria["fields"]["descricao"],
                u"dia": movbancaria["fields"]["dia"],
                u"valor": movbancaria["fields"]["valor"],
                u"pgto_cartao": movbancaria["fields"]["pgto_cartao"],
                u"categoria": id_nova_categoria(movbancaria),
            }
        }]

    def handle_dia(dia):
        del dia["fields"]["feriado"]
        return [dia]

    def handle_bandeira(bandeira):
        global BANDEIRAS__LAST_PK

        bandeira_nova_credito = {
            u"pk": BANDEIRAS__LAST_PK + 1,
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
            u"pk": BANDEIRAS__LAST_PK + 2,
            u"model": u"caixa.bandeira",
            u"fields": {
                u"ativa": True,
                u"nome": bandeira["fields"]["nome"] + u" Débito",
                u"taxa": bandeira["fields"]["taxa_debito"],
                u"prazo_de_deposito": 2,
                u"contagem_de_dias": "U",
                u"categoria": "D",
            },
        }

        BANDEIRAS__LAST_PK += 2

        BANDEIRAS__TABELA[bandeira["pk"]] = {
            "C": bandeira_nova_credito["pk"],
            "D": bandeira_nova_debito["pk"],
        }

        return bandeira_nova_credito, bandeira_nova_debito

    def handle_pagamentocomcartao(pagamentocomcartao):
        bandeira_antiga = pagamentocomcartao["fields"]["bandeira"]
        categoria = pagamentocomcartao["fields"]["categoria"]

        bandeira_nova = BANDEIRAS__TABELA[bandeira_antiga][categoria]

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
        ("caixa.dia", handle_dia),
        ("caixa.bandeira", handle_bandeira),
        ("caixa.pagamentocomcartao", handle_pagamentocomcartao),
        ("caixa.despesadecaixa", handle_despesadecaixa),
        ("caixa.movimentacaobancaria", handle_movimentacaobancaria),
    )

    not_to_be_converted = [e for e in dump if e['model'] not in [m[0] for m in model_and_function]]

    print("Convertendo modelos no formato antigo...")

    result = []

    for model, func in model_and_function:
        print("Convertendo modelo {model}".format(model=model))
        for elem in [e for e in dump if e['model'] == model]:
            result.extend(func(elem))

    result.extend(not_to_be_converted)

    print("Transformando resultado em JSON")

    return json.dumps(result)
