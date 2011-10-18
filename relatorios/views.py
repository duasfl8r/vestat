# -*- encoding: utf-8 -*-
import csv
import datetime

from vestat.caixa.models import *
from vestat.settings import *
from vestat.relatorios.forms import *

from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.db.models.aggregates import Sum, Avg, Count
from django.forms.forms import pretty_name
from django.utils.encoding import iri_to_uri

def somar_dict(accum, key, d):
    if key in accum:
        for k, v in d.items():
            accum[key][k] += v
    else:
        accum[key] = d

def anual(request):
    filtro_form = RelatorioAnualForm(request.GET)

    if filtro_form.is_valid():
        ano = filtro_form.cleaned_data.get("ano")

        anos = Dia.estruturar_dias()
        if int(ano) in anos:
            ano_estrutura = anos[int(ano)]
        else:
            ano_estrutura = { "nome": ano,
                              "faturamento": 0, "faturamento_acumulado": 0,
                              "despesas": 0, "despesas_acumulado": 0,
                              "resultado": 0, "resultado_acumulado": 0,
                              "meses": []}

        titulo = "Relatório anual: " + str(ano)

    else:
        ano_estrutura = None
        titulo = "Ano inválido"

    return render_to_response('relatorios/anual.html', {
                              'title': titulo,
                              'ano': ano_estrutura,
                              'filtro_form': filtro_form,
                              'voltar_link': '/relatorios/',
                              'voltar_label': 'Relatórios',
                             },
                             context_instance=RequestContext(request))

def simples(request):
    filtro_form = RelatorioSimplesForm(request.GET)
    if filtro_form.is_valid():
        filtro = filtro_form.cleaned_data
        dados = Dia.listar_dias(filtro.get("de"), filtro.get("ateh"))
    else:
        dados = Dia.listar_dias()

    return render_to_response('relatorios/simples.html', {
                              'title': "Relatório simples",
                              'dados': dados,
                              'filtro_form': filtro_form,
                              'voltar_link': '/relatorios/',
                              'voltar_label': 'Relatórios',
                             },
                             context_instance=RequestContext(request))


def vendas_por_mesa(dias):
    def split_and_strip(string, sep=","):
        """Splits a string using `sep` as a separator, and strips whitespace from the splitted results."""
        return map(lambda s: s.strip(), string.split(sep))
    
    def primeira_mesa(mesas):
        try:
            return int(split_and_strip(mesas)[0])
        except:
            return split_and_strip(mesas)[0]

    vendas = Venda.objects.filter(dia__in=dias)
    agrupado = vendas.values("mesa").order_by("mesa")
    dados = agrupado.annotate(vendas=Count("id"),
                              entrada=Sum("conta"),
                              pessoas=Sum("num_pessoas"),
                              permanencia_media=Avg("permanencia"))
    headers = ("mesa", "vendas", "entrada", "pessoas", "permanencia_media")

    for row in dados:
        row["permanencia_media"] = secs_to_time(row["permanencia_media"])
        row["mesa"] = row["mesa"].replace("/", ",")

    body = [[row[col] for col in headers] for row in dados]
    body.sort(key=lambda row: primeira_mesa(row[0]))

    return {
             "title": "Vendas por mesa",
             "headers": headers,
             "body": body
           }

def vendas_por_categoria(dias):
    vendas = Venda.objects.filter(dia__in=dias)
    agrupado = vendas.values("categoria")
    dados = agrupado.annotate(vendas=Count("id"),
                              entrada=Sum("conta"),
                              pessoas=Sum("num_pessoas"),
                              permanencia_media=Avg("permanencia"))
    headers = ("categoria", "vendas", "entrada", "pessoas", "permanencia_media")

    for row in dados:
        row["permanencia_media"] = secs_to_time(row["permanencia_media"])

    body = [[row[col] for col in headers] for row in dados]

    for row in body:
        row[0] = dict(Venda.CATEGORIA_CHOICES)[row[0]]

    return {
             "title": "Vendas por categoria",
             "headers": headers,
             "body": body
           }

def vendas_por_cidade(dias):
    vendas = Venda.objects.filter(dia__in=dias)
    agrupado = vendas.values("cidade_de_origem")
    dados = agrupado.annotate(vendas=Count("id"),
                              entrada=Sum("conta"),
                              pessoas=Sum("num_pessoas"),
                              permanencia_media=Avg("permanencia"))
    headers = ("cidade_de_origem", "vendas", "entrada", "pessoas", "permanencia_media")

    for row in dados:
        row["permanencia_media"] = secs_to_time(row["permanencia_media"])
        if not row["cidade_de_origem"]:
            row["cidade_de_origem"] = "---"

    body = [[row[col] for col in headers] for row in dados]

    return {
             "title": "Vendas por cidade",
             "headers": headers,
             "body": body
           }

def vendas_por_dia_da_semana(dias):
    vendas = Venda.objects.filter(dia__in=dias)

    agrupado = {}
    for venda in vendas:
        key = venda.dia.categoria_semanal()
        somar_dict(agrupado, key, { "vendas": 1,
                                    "entrada": venda.conta,
                                    "pessoas": venda.num_pessoas,
                                    "permanencia_media": venda.permanencia })

    dados = []
    headers = ("categoria_semanal", "vendas", "entrada", "pessoas", "permanencia_media")
    for grupo in agrupado.keys():
        row = {}

        row["categoria_semanal"] = grupo
        for i, header in enumerate(headers[1:]):
            row[header] = agrupado[grupo][header]

        row["permanencia_media"] = secs_to_time(row["permanencia_media"] / row["vendas"])
        dados.append(row)

    body = [[row[col] for col in headers] for row in dados]

    return {
             "title": "Vendas por dia de semana",
             "headers": headers,
             "body": body
           }

def pgtos_por_bandeira(dias):
    pgtos = PagamentoComCartao.objects.filter(venda__dia__in=dias)

    agrupado = {}
    for pgto in pgtos:
        key = (pgto.bandeira.nome, pgto.get_categoria_display())
        somar_dict(agrupado, key, { "pagamentos": 1,
                                     "entrada": pgto.valor,
                                   })

    dados = []
    for grupo in agrupado.keys():
        row = {}
        row["bandeira"] = "%s %s" % (grupo[0], grupo[1])
        row["pagamentos"] = agrupado[grupo]["pagamentos"]
        row["entrada"] = agrupado[grupo]["entrada"]
        dados.append(row)

    headers = ("bandeira", "pagamentos", "entrada")

    body = [[row[col] for col in headers] for row in dados]

    return {
             "title": "Pagamentos com cartão por bandeira",
             "headers": headers,
             "body": body
           }

def despesas_por_categoria(dias):
    despesas = DespesaDeCaixa.objects.filter(dia__in=dias)
    agrupado = despesas.values("categoria")
    dados = agrupado.annotate(despesas=Count("id"),
                              total=Sum("valor"))
    headers = ("categoria", "despesas", "total")

    body = [[row[col] for col in headers] for row in dados]

    for row in body:
        row[0] = dict(DespesaDeCaixa.CATEGORIA_CHOICES)[row[0]]

    return {
             "title": "Despesas de caixa por categoria",
             "headers": headers,
             "body": body
           }

def movbancarias_por_categoria(dias):
    movbancarias = MovimentacaoBancaria.objects.filter(dia__in=dias)
    agrupado = movbancarias.values("categoria")
    dados = agrupado.annotate(movbancarias=Count("id"),
                              total=Sum("valor"))
    headers = ("categoria", "movbancarias", "total")

    body = [[row[col] for col in headers] for row in dados]

    for row in body:
        row[0] = dict(MovimentacaoBancaria.CATEGORIA_CHOICES)[row[0]]

    return {
             "title": "Movimentações bancárias por categoria",
             "headers": headers,
             "body": body
           }


def view_relatorio(request, titulo, tablemakers):
    filtro_form = RelatorioSimplesForm(request.GET)

    if filtro_form.is_valid():
        filtro = filtro_form.cleaned_data
        de = filtro.get("de")
        ateh = filtro.get("ateh")
        dias = Dia.dias_entre(de, ateh)
    else:
        dias = Dia.objects.all()
        de = ateh = None

    titulo = titulo or ""
    if de:
        titulo += ", de: " + str(de)
    if ateh:
        titulo += ", ateh: " + str(ateh)

    tables = []
    for tablemaker in tablemakers:
        table = tablemaker(dias)

        table["headers"] = map(pretty_name, table["headers"])

        tables.append(table)
    
    if "csv" in request.GET:
        response = render_to_response('relatorios/csv.html', {
                              'title': titulo,
                              'tables': tables,
                             },
                             context_instance=RequestContext(request),
                             mimetype="text/csv")

        response['Content-Disposition'] = 'attachment; filename=dados_por_mesa.csv'
        print response['Content-Type']
        return response


    return render_to_response('relatorios/table.html', {
                              'title': titulo,
                              'filtro_form': filtro_form,
                              'tables': tables,
                              'request': request,
                              'voltar_link': '/relatorios/',
                              'voltar_label': 'Relatórios',
                             },
                             context_instance=RequestContext(request))


def ajustes(request):
    ajustes = AjusteDeCaixa.objects.all()
    ajustes_pos = ajustes.filter(valor__gt=0)
    ajustes_neg = ajustes.filter(valor__lt=0)
    
    if ajustes_pos:
        positivo = ajustes_pos.aggregate(Sum('valor'))['valor__sum']
    else:
        positivo = 0
    
    if ajustes_neg:
        negativo = ajustes_neg.aggregate(Sum('valor'))['valor__sum']
    else:
        negativo = 0
    
    dados = {
              'ajustes': ajustes,
              'positivo': positivo,
              'negativo': negativo,
              'total': ajustes.aggregate(Sum('valor'))['valor__sum'],
            }
    
    return render_to_response('relatorios/ajustes.html', {
                              'title': "Ajustes de caixa",
                              'dados': dados,
                              'voltar_link': '/relatorios/',
                              'voltar_label': 'Relatórios',
                             },
                             context_instance=RequestContext(request))

def index(request):
    hoje = datetime.date.today()
    inicio_do_mes = datetime.date(hoje.year, hoje.month, 1)
    
    relatorio_simples_form = RelatorioSimplesForm({'de': inicio_do_mes.strftime("%d/%m/%y"),
                                                   'ateh': hoje.strftime("%d/%m/%y"), })
    relatorio_anual_form = RelatorioAnualForm({ 'ano': hoje.year, })
    return render_to_response('relatorios/index.html', {
                                'title': "Relatórios",
                                'relatorio_simples_form': relatorio_simples_form,
                                'relatorio_anual_form': relatorio_anual_form,
                                  'voltar_link': '/',
                                  'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))
