# -*- encoding: utf-8 -*-
import datetime
from decimal import Decimal
import logging

import numpy
from matplotlib import pyplot

from vestat.caixa.models import Dia, Venda, DespesaDeCaixa, \
    PagamentoComCartao, AjusteDeCaixa, MovimentacaoBancaria, \
    secs_to_time, MESES

from vestat.caixa.templatetags.vestat_extras import colorir_num
from vestat.relatorios.forms import RelatorioAnualForm, RelatorioSimplesForm, AnoFilterForm, DateFilterForm, IntervaloMesesFilterForm
from vestat.relatorios.reports import Table, Report, TableField
from vestat.django_utils import format_currency, format_date
from vestat.temp import mkstemp, path2url

from vestat.relatorios.reports2 import Report2, ReportElement
from vestat.relatorios.reports2.elements import Table2, TableField2

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models.aggregates import Sum, Avg, Count
from django.forms.forms import pretty_name
from django.views.generic import View

logger = logging.getLogger(__name__)

def somar_dict(accum, key, d):
    if key in accum:
        for k, v in d.items():
            accum[key][k] += v
    else:
        accum[key] = d

class ReportView(View):
    """
    Uma classe abstrata pra uma view de relatório.

    Subclasses devem implementar o método `get_raw_data` e sobrescrever
    o atributo `Report`. Para ter um formulário de filtragem dos dados,
    deve sobrescrever o atributo `FilterForm`.
    """

    Report = None
    """
    Classe de relatórios usada pela view. Deve ser subclasse de `reports2.Report2`.
    """

    FilterForm = None
    """
    Classe do formulário de filtragem usado. Deve ser subclasse de `reports.FilterForm`.
    """

    def get_raw_data(self):
        """
        Extrai os dados crus a serem filtrados pelo
        formulário `FilterForm` e enviados pro relatório `Report`.
        """
        pass

    def get(self, request, *args, **kwargs):
        """
        Extrai os dados crus, filtra se houver um `FilterForm`, cria o
        objeto `Report` e o renderiza.
        """
        if self.FilterForm:
            filter_form = self.FilterForm(data=request.GET)

            if filter_form.is_valid():
                data = filter_form.filter(self.get_raw_data())
            else:
                data = []

            subtitle = filter_form.filter_info
        else:
            filter_form = None
            data = self.get_raw_data()
            subtitle = ""

        report = self.Report(data)
        format = request.GET.get("format", "html")
        report_contents = report.render(format)

        template_name = "report2_view.{0}".format(format)

        response = render_to_response(template_name, {
              'title': report.title,
              'subtitle': subtitle,
              'report_contents': report_contents,
              'filter_form': filter_form, },
             context_instance=RequestContext(request))

        if format == "csv":
            response.mimetype = "text/csv"
            response['Content-Disposition'] = 'attachment; filename=anual.csv'

        return response


class DespesasPorMesChart(ReportElement):
    title = "Gráfico de despesas"

    def render_html(self):
        despesas = []
        xlabels = []

        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                despesas_total = Dia.despesas_de_caixa_total(dias) + Dia.debitos_bancarios_total(dias)
                despesas.append(-despesas_total)
                xlabels.append("{:%m/%Y}".format(datetime.date(ano, mes, 1)))

        # nenhuma despesa, nenhuma imagem
        if not despesas:
            return u''

        x_locations = numpy.arange(len(despesas))

        bar_width = 0.5
        min_width = 4
        padding = 0.3

        adjustments = {
            "bottom": 0.1,
            "left": 0.17,
        }

        plot_width = max(bar_width * len(despesas), min_width) + sum(adjustments.values())

        figsize = (plot_width, 6)

        try:
            figure = pyplot.figure(figsize=figsize)
            ax = figure.add_subplot(111)

            pyplot.subplots_adjust(**adjustments)

            rects = ax.bar(x_locations, despesas, bar_width, color='r')

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Despesas totais por mês")
            ax.set_xticks(x_locations + padding)
            ax.set_xticklabels(xlabels)
            ax.set_xlim([0 - padding, len(despesas)])

            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1, y2 * 1.1)

            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                # attach some text labels
                for rect in rects:
                    height = rect.get_height()

                    text_x = rect.get_x() + rect.get_width() / 2.0

                    if rect.get_y() < 0:
                        text_y = -1 * (height + 900)
                    else:
                        text_y = height + 400

                    ax.text(text_x, text_y, "{0}".format(format_currency(height)),
                            ha='center', va='bottom', size='8')


            autolabel(ax, rects)

            img_file, img_path = mkstemp(suffix=".png")
            img_url = path2url(img_path)
            figure.savefig(img_path, format="png")

            return u'<img src="{img_url}" />'.format(img_url=img_url)

        finally:
            pyplot.close(figure)


class FaturamentoPorMesChart(ReportElement):
    title = "Gráfico de faturamentos"

    def render_html(self):
        faturamentos = []
        xlabels = []

        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                faturamento_total = Dia.faturamento_total(dias)
                faturamentos.append(faturamento_total)
                xlabels.append("{:%m/%Y}".format(datetime.date(ano, mes, 1)))

        # nenhum faturamento, nenhuma imagem
        if not faturamentos:
            return u''

        x_locations = numpy.arange(len(faturamentos))

        bar_width = 0.5
        min_width = 4
        padding = 0.3

        adjustments = {
            "bottom": 0.1,
            "left": 0.17,
        }

        plot_width = max(bar_width * len(faturamentos), min_width) + sum(adjustments.values())

        figsize = (plot_width, 6)

        try:
            figure = pyplot.figure(figsize=figsize)
            ax = figure.add_subplot(111)

            pyplot.subplots_adjust(**adjustments)

            rects = ax.bar(x_locations, faturamentos, bar_width, color='g')

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Faturamento total por mês")
            ax.set_xticks(x_locations + padding)
            ax.set_xticklabels(xlabels)
            ax.set_xlim([0 - padding, len(faturamentos)])

            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1, y2 * 1.1)

            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                # attach some text labels
                for rect in rects:
                    height = rect.get_height()

                    text_x = rect.get_x() + rect.get_width() / 2.0

                    if rect.get_y() < 0:
                        text_y = -1 * (height + 900)
                    else:
                        text_y = height + 400

                    ax.text(text_x, text_y, "{0}".format(format_currency(height)),
                            ha='center', va='bottom', size='8')


            autolabel(ax, rects)

            img_file, img_path = mkstemp(suffix=".png")
            img_url = path2url(img_path)
            figure.savefig(img_path, format="png")
            return u'<img src="{img_url}" />'.format(img_url=img_url)

        finally:
            pyplot.close(figure)


class ResultadoPorMesChart(ReportElement):
    title = "Gráfico de resultados"

    def render_html(self):
        resultados = []
        xlabels = []
        colors = []

        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                resultado_total = Dia.resultado_total(dias)
                resultados.append(resultado_total)
                xlabels.append("{:%m/%Y}".format(datetime.date(ano, mes, 1)))
                colors.append("g" if resultado_total > 0 else "r")

        # nenhum resultado, nenhuma imagem
        if not resultados:
            return u''

        x_locations = numpy.arange(len(resultados))

        bar_width = 0.5
        min_width = 4
        padding = 0.3

        adjustments = {
            "bottom": 0.1,
            "left": 0.17,
        }

        plot_width = max(bar_width * len(resultados), min_width) + sum(adjustments.values())

        figsize = (plot_width, 6)

        try:
            figure = pyplot.figure(figsize=figsize)
            ax = figure.add_subplot(111)

            pyplot.subplots_adjust(**adjustments)

            rects = ax.bar(x_locations, resultados, bar_width, color=colors)

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Resultado total por mês")
            ax.set_xticks(x_locations + padding)
            ax.set_xticklabels(xlabels)
            ax.set_xlim([0 - padding, len(resultados)])

            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1 * 1.1, y2 * 1.1)

            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                # attach some text labels
                for rect in rects:
                    height = rect.get_height()

                    text_x = rect.get_x() + rect.get_width() / 2.0

                    if rect.get_y() < 0:
                        height *= -1
                        text_y = height - 500
                    else:
                        text_y = height + 200

                    ax.text(text_x, text_y, "{0}".format(format_currency(height)),
                            ha='center', va='bottom', size='8')


            autolabel(ax, rects)

            img_file, img_path = mkstemp(suffix=".png")
            img_url = path2url(img_path)
            figure.savefig(img_path, format="png")
            return u'<img src="{img_url}" />'.format(img_url=img_url)

        finally:
            pyplot.close(figure)


class MesesReportTable(Table2):
    """
    Tabela pro relatório anual.
    """
    title = "Tabela"

    fields = (
        TableField2("Mês"),
        TableField2("Pessoas", slug="num_pessoas", classes=["number"]),
        TableField2("Vendas", classes=["number"]),
        TableField2("Perm Média", slug="permanencia_media", classes=["time"]),
        TableField2("Faturamento", classes=["currency"]),
        TableField2("Desp Cx", slug="despesas_de_caixa", classes=["currency"]),
        TableField2("Desp Banco", slug="debitos_bancarios", classes=["currency"]),
        TableField2("Resultado", slug="resultado", classes=["currency"]),
        TableField2("Per Capita", slug="per_capita", classes=["currency"]),
        TableField2("10%", slug="gorjeta", classes=["currency"]),
    )

    @property
    def body(self):
        result = []
        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                result.append(["%04d-%02d" % (ano, mes),              # mes
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

        return sorted(result, key=lambda r: r[0])


class AnualReport(Report2):
    """
    Relatório anual.
    """
    title="Relatório anual"
    element_classes = [DespesasPorMesChart, FaturamentoPorMesChart, MesesReportTable]


class AnualReportView(ReportView):
    """
    Class-based view do relatório anual.
    """
    Report = AnualReport
    FilterForm = AnoFilterForm

    def get_raw_data(self):
        return Dia.objects.all()


class MesesReport(Report2):
    """
    Relatório de meses.
    """
    title="Relatório de meses"
    element_classes = [DespesasPorMesChart, FaturamentoPorMesChart, ResultadoPorMesChart, MesesReportTable]


class MesesReportView(ReportView):
    """
    Class-based view do relatório de meses.
    """
    Report = MesesReport
    FilterForm = IntervaloMesesFilterForm

    def get_raw_data(self):
        return Dia.objects.all()


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
        from_date = filter_form.cleaned_data.get("from_date").strftime(settings.SHORT_DATE_FORMAT_PYTHON)
        to_date = filter_form.cleaned_data.get("to_date").strftime(settings.SHORT_DATE_FORMAT_PYTHON)
        title = "Despesas: {from_date} - {to_date}".format(**vars())
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
        row["entrada"] = format_currency(row["entrada"])
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
        row["entrada"] = format_currency(row["entrada"])
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
        row["entrada"] = format_currency(row["entrada"])
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

        row["entrada"] = format_currency(row["entrada"])
        if row["permanencia_media"]:
            row["permanencia_media"] = secs_to_time(row["permanencia_media"] / row["vendas"])
        else:
            row["permanencia_media"] = 0
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
        key = (pgto.bandeira.nome)
        somar_dict(agrupado, key, { "pagamentos": 1,
                                     "entrada": pgto.valor,
                                   })

    dados = []
    for grupo in agrupado.keys():
        row = {}
        row["bandeira"] = grupo
        row["pagamentos"] = agrupado[grupo]["pagamentos"]
        row["entrada"] = format_currency(agrupado[grupo]["entrada"])
        dados.append(row)

    headers = ("bandeira", "pagamentos", "entrada")

    body = [[row[col] for col in headers] for row in dados]

    return {
             "title": "Pagamentos com cartão por bandeira",
             "headers": headers,
             "body": body
           }

def despesas_por_categoria(dias):
    """
    Retorna um relatório de despesas agrupadas por categoria,
    representado por um dicionário.

    Exibe, pra cada categoria, no período designado:

    - A quantidade de despesas

    - O valor das despesas

    - O percentual das despesas com relação à despesa total de todas as
      categorias

    - O percentual das despesas com relação ao total de vendas
      do mesmo período.

    Exibe um rodapé com o total de despesas de todas as categorias.

    """
    headers = ("categoria", "despesas", "total", "porcentagem_das_despesas", "porcentagem_das_vendas",)

    despesas = list(DespesaDeCaixa.objects.filter(dia__in=dias)) + \
            list(MovimentacaoBancaria.objects.filter(dia__in=dias, valor__lt=0))

    qtd_despesas = len(despesas)
    total_despesas = Decimal(sum(d.valor for d in despesas))

    vendas = Venda.objects.filter(dia__in=dias)
    total_vendas = Decimal(sum(v.conta for v in vendas))

    # Acumula a qtd e o total em um dicionário
    agrupado_dict = {}
    for despesa in despesas:
        categoria = agrupado_dict.setdefault(
            despesa.categoria,
            {
                "despesas": 0,
                "total": Decimal("0"),
                "porcentagem_das_despesas": 0,
            })

        categoria["total"] += despesa.valor
        categoria["despesas"] += 1

    # Calcula porcentagem em relação à despesa total
    for categoria in agrupado_dict.values():
        razao_das_despesas = abs(categoria["total"] / total_despesas)
        razao_das_vendas = abs(categoria["total"] / total_vendas)

        categoria["porcentagem_das_despesas"] = "{:.2%}".format(razao_das_despesas)
        categoria["porcentagem_das_vendas"] = "{:.2%}".format(razao_das_vendas)

    # Produz uma lista de tuplas a partir do dicionário
    nome = lambda cat: dict(DespesaDeCaixa.CATEGORIA_CHOICES)[cat]
    agrupado_list = [
        (
            nome(cat),
            row["despesas"],
            format_currency(row["total"]),
            row["porcentagem_das_despesas"],
            row["porcentagem_das_vendas"],
        ) for cat, row in agrupado_dict.items()
    ]

    body = sorted(agrupado_list, key=lambda r: r[2]) # Ordem decrescente de valor

    footer = [
        ("TOTAL", qtd_despesas, total_despesas, "100%", "-")
    ]

    return {
             "title": "Despesas por categoria",
             "headers": headers,
             "body": body,
             "footer": footer
           }

def movbancarias_por_categoria(dias):
    movbancarias = MovimentacaoBancaria.objects.filter(dia__in=dias)
    agrupado = movbancarias.values("categoria")
    dados = agrupado.annotate(movbancarias=Count("id"),
                              total=Sum("valor"))
    headers = ("categoria", "movbancarias", "total")

    body = [[row[col] for col in headers] for row in dados]

    for row in body:
        row["movbancarias"] = format_currency(row["movbancarias"])
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
        titulo += ", de: " + format_date(de)
    if ateh:
        titulo += ", ateh: " + format_date(ateh)

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
