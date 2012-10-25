# -*- encoding: utf-8 -*-
import csv
import datetime

from vestat.caixa.models import *
from vestat.caixa.templatetags.vestat_extras import colorir_num
from vestat.settings import *
from vestat.relatorios.forms import *
from vestat.relatorios.reports import Table, Report, AnoFilterForm, DateFilterForm, TableField

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
    def process_data(self, data):
        for ano in Dia._anos(data):
            for mes in Dia._meses(ano, data):
                dias = Dia._dias(ano, mes, data)
                self.append(["%04d-%02d" % (ano, mes),              # mes
                             Dia.num_pessoas_total(dias),           # num pessoas
                             colorir_num(Dia.vendas_total(dias)),                # vendas
                             Dia.permanencia_media_total(dias),     # permanencia medi
                             colorir_num(Dia.faturamento_total(dias)),           # faturamento
                             colorir_num(Dia.despesas_de_caixa_total(dias)),     # desp cx
                             colorir_num(Dia.debitos_bancarios_total(dias)),     # banco
                             colorir_num(Dia.resultado_total(dias)),             # resultado
                             colorir_num(Dia.captacao_por_pessoa_total(dias)),   # per capita
                             colorir_num(Dia.gorjeta_total(dias)),               # 10%
                             ])

            self = self.sort(0)

    table = Table(fields=[
                TableField("Mês"),
                TableField("Pessoas", slug="num_pessoas", classes=["number"]),
                TableField("Vendas", classes=["number"]),
                TableField("Perm Média", slug="permanencia_media", classes=["time"]),
                TableField("Faturamento", classes=["currency"]),
                TableField("Desp Cx", slug="despesas_de_caixa", classes=["currency"]),
                TableField("Desp Banco", slug="debitos_bancarios", classes=["currency"]),
                TableField("Resultado", slug="resultado", classes=["currency"]),
                TableField("Per Capita", slug="per_capita", classes=["currency"]),
                TableField("10%", slug="gorjeta", classes=["currency"]),
            ],
            process_data=process_data,
    )

    filter_form = AnoFilterForm(data=request.GET, datefield_name="data")

    if filter_form.is_valid():
        report = Report(data=Dia.objects.all(), filters=[filter_form], tables=[table])
        title = "Relatório anual: " + str(filter_form.cleaned_data.get("ano"))
    else:
        report = None
        title = "Ano inválido"


    if "csv" in request.GET:
        response = render_to_response('relatorios/report_csv.html', {
                              'report': report,
                              'title': title,
                             },
                             context_instance=RequestContext(request),
                             mimetype="text/csv")

        response['Content-Disposition'] = 'attachment; filename=anual.csv'
        return response


    return render_to_response('relatorios/report.html', {
                              'report': report,
                              'title': title,
                              'filter_form': filter_form,
                              'voltar_link': '/relatorios/',
                              'voltar_label': 'Relatórios',
                             },
                             context_instance=RequestContext(request))
def lista_despesas(request):
    def process_data(self, data):
        def make_row(dia, despesa, tipo):
            return ["<a href=\"%s\">%02d/%02d/%04d</a>" % (dia.get_absolute_url(),
                                                           dia.data.day, dia.data.month,
                                                           dia.data.year),
                    colorir_num(despesa.valor),
                    despesa.get_categoria_display(),
                    tipo]

        for dia in data.order_by("data"):
            for despesa_cx in dia.despesadecaixa_set.all():
                self.append(make_row(dia, despesa_cx, "Caixa"))
            for despesa_bc in dia.movimentacaobancaria_set.filter(valor__lt=0):
                self.append(make_row(dia, despesa_bc, "Banco"))

    table = Table(fields=[
                TableField("Dia"),
                TableField("Valor", classes=["currency"]),
                TableField("Categoria"),
                TableField("C/B?"),            ],
            process_data=process_data,
    )
    
    filter_form = DateFilterForm(data=request.GET, datefield_name="data")

    if filter_form.is_valid():
        report = Report(data=Dia.objects.all(), filters=[filter_form], tables=[table])
        title = "Despesas: %s - %s" % (str(filter_form.cleaned_data.get("from_date")),
                                       str(filter_form.cleaned_data.get("to_date")))
    else:
        report = None
        title = "Período inválido"

    if "csv" in request.GET:
        response = render_to_response('relatorios/report_csv.html', {
                              'report': report,
                              'title': title,
                             },
                             context_instance=RequestContext(request),
                             mimetype="text/csv")

        response['Content-Disposition'] = 'attachment; filename=despesas.csv'
        return response


    return render_to_response('relatorios/report.html', {
                              'report': report,
                              'title': title,
                              'filter_form': filter_form,
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
    despesas = list(DespesaDeCaixa.objects.filter(dia__in=dias)) + \
            list(MovimentacaoBancaria.objects.filter(dia__in=dias, valor__lt=0))

    despesas_dict = {}

    for despesa in despesas:
        row_dict = despesas_dict.setdefault(despesa.categoria, {"despesas": 0, "total": Decimal("0")})
        row_dict["total"] += despesa.valor
        row_dict["despesas"] += 1

    headers = ("categoria", "despesas", "total")

    body = [[key, row["despesas"], row["total"]] for key, row in despesas_dict.items()]

    body.sort(key=lambda r: r[2])

    for row in body:
        row[0] = dict(DespesaDeCaixa.CATEGORIA_CHOICES)[row[0]]

    return {
             "title": "Despesas por categoria",
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
    
    relatorio_simples_form = RelatorioSimplesForm({'de': inicio_do_mes.strftime("%d/%m/%Y"),
                                                   'ateh': hoje.strftime("%d/%m/%Y"), })
    relatorio_anual_form = RelatorioAnualForm({ 'ano': hoje.year, })
    ano_filter_form = AnoFilterForm(initial={"ano": hoje.strftime("%Y")}, datefield_name="data")
    date_filter_form = DateFilterForm(initial={
                                        "from_date": inicio_do_mes.strftime("%d/%m/%Y"),
                                        "to_date": hoje.strftime("%d/%m/%Y"),
                                      }, datefield_name="data")

    return render_to_response('relatorios/index.html', {
                                'title': "Relatórios",
                                'relatorio_simples_form': relatorio_simples_form,
                                'relatorio_anual_form': relatorio_anual_form,
                                'ano_filter_form': ano_filter_form,
                                'date_filter_form': date_filter_form,
                                  'voltar_link': '/',
                                  'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))
