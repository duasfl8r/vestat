# -*- encoding: utf-8 -*-
import datetime
from decimal import Decimal
from collections import defaultdict
import logging

import numpy
from matplotlib import pyplot

from vestat.caixa.models import Dia, Venda, DespesaDeCaixa, \
    PagamentoComCartao, AjusteDeCaixa, MovimentacaoBancaria, \
    secs_to_time, CategoriaDeMovimentacao

from vestat.caixa.templatetags.vestat_extras import colorir_num
from vestat.relatorios.forms import RelatorioSimplesForm, AnoFilterForm, DateFilterForm, DateFilterForm2, IntervaloMesesFilterForm
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
            response['Content-Disposition'] = 'attachment; filename=report.csv'

        return response


class DespesasPorMesChart(ReportElement):
    """
    Gera gráfico de barras de despesas de cada mês, e uma linha de tendência.

    Gráfico de barras:

    - eixo X -> meses
    - eixo Y -> total de despesas de cada mês

    """

    title = "Gráfico de despesas"

    def render_html(self):
        """
        Renderiza o gráfico em HTML, usando o matplotlib.

        """

        despesas = []
        xlabels = []

        # monta a lista de despesas totais por mês, iterando pelos anos
        # e meses dos dias fornecidos como dados crus.
        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                despesas_total = Dia.despesas_de_caixa_total(dias) + Dia.debitos_bancarios_total(dias)
                despesas.append(-despesas_total)
                xlabels.append("{:%m/%Y}".format(datetime.date(ano, mes, 1)))

        # nenhuma despesa => nenhuma imagem
        if not despesas:
            return u''

        x_locations = numpy.arange(len(despesas))

        # largura de cada barra (inches)
        bar_width = 0.5
        # largura mínima do gráfico (inches)
        min_width = 4
        # espaçamento entre uma barra e outra (inches)
        padding = 0.3

        # ajustes de espaçamento ao redor do gráfico (porcentagem de
        # width/height)
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

            # Gráfico de barras
            rects = ax.bar(x_locations, despesas, bar_width, color='r')

            # Linha de tendência
            slope, intercept = numpy.polyfit(x_locations, map(float, despesas), 1)
            trendline_y = intercept + (slope * x_locations)
            line = ax.plot(x_locations, trendline_y, color="blue")

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Despesas totais por mês")
            ax.set_xticklabels(xlabels)

            # espaçamento à direita de todas as barras
            ax.set_xticks(x_locations + padding)
            # espaçamento à esquerda da primeira barra
            ax.set_xlim([0 - padding, len(despesas)])

            # deixa o eixo Y um pouco maior, pra dar espaço pro rótulo
            # em cima de cada barra
            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1, y2 * 1.1)

            # configura rotação e tamanho do rótulo de cada mês no eixo X
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                """
                Rotula cada uma das barras com seu valor correspondente
                (ie total de despesas do mês)
                """

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
    """
    Gera gráfico de barras de faturamento de cada mês, e uma linha de tendência.

    Gráfico de barras:

    - eixo X -> meses
    - eixo Y -> faturamento de cada mês

    """

    title = "Gráfico de faturamentos"

    def render_html(self):
        """
        Renderiza o gráfico em HTML, usando o matplotlib.

        """
        faturamentos = []
        xlabels = []

        # monta a lista de faturamento total por mês, iterando pelos anos
        # e meses dos dias fornecidos como dados crus.
        for ano in Dia._anos(self.data):
            for mes in Dia._meses(ano, self.data):
                dias = Dia._dias(ano, mes, self.data)
                faturamento_total = Dia.faturamento_total(dias)
                faturamentos.append(faturamento_total)
                xlabels.append("{:%m/%Y}".format(datetime.date(ano, mes, 1)))

        # nenhum faturamento => nenhuma imagem
        if not faturamentos:
            return u''

        x_locations = numpy.arange(len(faturamentos))

        # largura de cada barra (inches)
        bar_width = 0.5
        # largura mínima do gráfico (inches)
        min_width = 4
        # espaçamento entre uma barra e outra (inches)
        padding = 0.3

        # ajustes de espaçamento ao redor do gráfico (porcentagem de
        # width/height)
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

            # Gráfico de barras
            rects = ax.bar(x_locations, faturamentos, bar_width, color='g')

            # Linha de tendência
            slope, intercept = numpy.polyfit(x_locations, map(float, faturamentos), 1)
            trendline_y = intercept + (slope * x_locations)
            line = ax.plot(x_locations, trendline_y, color="blue")

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Faturamento total por mês")
            ax.set_xticklabels(xlabels)

            # espaçamento à direita de todas as barras
            ax.set_xticks(x_locations + padding)
            # espaçamento à esquerda da primeira barra
            ax.set_xlim([0 - padding, len(faturamentos)])

            # deixa o eixo Y um pouco maior, pra dar espaço pro rótulo
            # em cima de cada barra
            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1, y2 * 1.1)

            # configura rotação e tamanho do rótulo de cada mês no eixo X
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                """
                Rotula cada uma das barras com seu valor correspondente
                (ie faturamento do mês)
                """

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
    """
    Gera gráfico de barras de resultado de cada mês, e uma linha de tendência.

    Gráfico de barras:

    - eixo X -> meses
    - eixo Y -> resultado (faturamento menos as despesas) de cada mês

    """

    title = "Gráfico de resultados"

    def render_html(self):
        """
        Renderiza o gráfico em HTML, usando o matplotlib.

        """
        resultados = []
        xlabels = []
        colors = []

        # monta a lista de despesas totais por mês, iterando pelos anos
        # e meses dos dias fornecidos como dados crus.
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

        # largura de cada barra (inches)
        bar_width = 0.5
        # largura mínima do gráfico (inches)
        min_width = 4
        # espaçamento entre uma barra e outra (inches)
        padding = 0.3

        # ajustes de espaçamento ao redor do gráfico (porcentagem de
        # width/height)
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

            # Gráfico de barras
            rects = ax.bar(x_locations, resultados, bar_width, color=colors)

            # Linha de tendência
            slope, intercept = numpy.polyfit(x_locations, map(float, resultados), 1)
            trendline_y = intercept + (slope * x_locations)
            line = ax.plot(x_locations, trendline_y, color="blue")

            ax.set_ylabel(u"Reais")
            ax.set_title(u"Resultado total por mês")
            ax.set_xticklabels(xlabels)

            # espaçamento à direita de todas as barras
            ax.set_xticks(x_locations + padding)
            # espaçamento à esquerda da primeira barra
            ax.set_xlim([0 - padding, len(resultados)])

            # deixa o eixo Y um pouco maior, pra dar espaço pro rótulo
            # em cima de cada barra
            x1, x2, y1, y2 = pyplot.axis()
            ax.set_ylim(y1, y2 * 1.1)

            # configura rotação e tamanho do rótulo de cada mês no eixo X
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_rotation_mode("anchor")
                label.set_verticalalignment("top")
                label.set_horizontalalignment("right")
                label.set_size("8")

            def autolabel(ax, rects):
                """
                Rotula cada uma das barras com seu valor correspondente
                (ie resultado do mês)
                """

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
    Tabela pro relatório de meses. Cada linha da tabela exibe a
    consolidação dos dados de cada mês

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
                             Dia.vendas_total(dias),                # vendas
                             Dia.permanencia_media_total(dias),     # permanencia medi
                             colorir_num(Dia.faturamento_total(dias)),           # faturamento
                             colorir_num(Dia.despesas_de_caixa_total(dias)),     # desp cx
                             colorir_num(Dia.debitos_bancarios_total(dias)),     # banco
                             colorir_num(Dia.resultado_total(dias)),             # resultado
                             colorir_num(Dia.captacao_por_pessoa_total(dias)),   # per capita
                             colorir_num(Dia.gorjeta_total(dias)),               # 10%
                             ])

        return sorted(result, key=lambda r: r[0])



class MesesReport(Report2):
    """
    Relatório de meses.

    Elementos:

        - Gráfico de barras de despesas por mês
        - Gráfico de barras de faturamento por mês
        - Gráfico de barras de resultado por mês
        - Tabela com vários dados por mês.

    """

    title="Relatório de meses"
    element_classes = [DespesasPorMesChart, FaturamentoPorMesChart, ResultadoPorMesChart, MesesReportTable]


class MesesReportView(ReportView):
    """
    Class-based view do relatório de meses. Filtra os dias por mês/ano
    de início e mês/ano de fim.

    """

    Report = MesesReport
    FilterForm = IntervaloMesesFilterForm

    def get_raw_data(self):
        return Dia.objects.all()


def lista_despesas(request):
    def process_data(self, data):
        def make_row(dia, despesa, tipo):
            return ["<a href=\"%s\">%02d/%02d/%04d</a>" % (dia.get_absolute_url(),
                                                           dia.data.day, dia.data.month,
                                                           dia.data.year),
                    colorir_num(despesa.valor),
                    unicode(despesa.categoria),
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


class DespesasPorCategoriaCharts(ReportElement):
    """
    Gera gráficos de torta sobre o total de despesas, com a porcentagem
    de cada categoria.

    Gera um gráfico pra 'raiz' (categorias sem mãe), e um gráfico pra
    cada categoria que tenha filhas, com as porcentagens das despesas
    das filhas com relação à mãe.

    """

    title = "Gráficos de torta"

    def render_html(self):
        """
        Renderiza o gráfico em HTML, usando o matplotlib.

        """

        def arvore_categorias(categorias):
            """
            Retorna uma lista representando a árvore de categorias.

            A lista tem como elementos dicionários, cada um
            representando uma categoria e contendo as seguintes chaves:

                - nome: o nome da categoria
                - porcentagem: a porcentagem que essa categoria
                  contribui pro total de despesas de sua categoria-mãe
                  (ou pro total de todas as despesas, caso a categoria
                  não tenha mãe).
                - filhos: uma lista de dicionários com essas mesmas
                  chaves, representando as categorias-filhas dessa
                  categoria.

            """
            despesas = list(DespesaDeCaixa.objects.filter(dia__in=self.data, categoria__in=categorias)) + \
                    list(MovimentacaoBancaria.objects.filter(dia__in=self.data, valor__lt=0, categoria__in=categorias))
            total_despesas_das_categorias = Decimal(sum(d.valor for d in despesas))

            output_total = []

            for categoria in categorias:
                despesas_da_categoria = [d for d in despesas if d.categoria == categoria]
                total_despesas_da_categoria = Decimal(sum(d.valor for d in despesas_da_categoria))

                output_categoria = {
                    "nome": categoria.nome,
                    "porcentagem": total_despesas_da_categoria / total_despesas_das_categorias,
                }

                output_total.append(output_categoria)

                if categoria.filhas.count():
                    output_categoria["filhos"] = arvore_categorias(list(categoria.filhas.all()))

            output_total.sort(key=lambda c: c["porcentagem"], reverse=True)

            return output_total

        categorias = CategoriaDeMovimentacao.objects.all()
        categorias_raiz = [c for c in categorias if not c.mae]

        arvore = arvore_categorias(categorias_raiz)


        def montar_listas(nome, arvore, listas):
            """
            Transforma a árvore de categorias em uma lista de
            dicionários não-recursiva.

            Cada dicionário dessa lista representa categorias-irmã --
            categorias que são filhas da mesma mãe, e no caso da raiz,
            categorias que não têm mãe. Eles possuem as seguintes chaves:

                - mae: o nome da categoria-mãe, ou "Raiz" caso não haja
                  mãe.

                - irmas: uma lista de dicionários, cada um com as
                  seguintes chaves:

                    - nome: o nome da categoria

                    - porcentagem: a porcentagem que essa categoria
                      contribui pro total de despesas de sua categoria-mãe
                      (ou pro total de todas as despesas, caso a categoria
                      não tenha mãe).

            Categorias com porcentagem menor que a designada na variável
            `LIMITE` são agrupadas sob o rótulo "Outros", pra evitar que
            sejam exibidas diversas frações da torta muito pequenas e
            seus rótulos se embaralhem.
            """

            LIMITE = Decimal("0.05")

            lista = { "mae": nome, "irmas": [] }
            listas.append(lista)

            for categoria in arvore:
                if categoria["porcentagem"] > LIMITE:
                    lista["irmas"].append({ "nome": categoria["nome"], "porcentagem": categoria["porcentagem"] })
                else:
                    if lista["irmas"][-1]["nome"] == "Outros":
                        outros = lista["irmas"][-1]
                    else:
                        outros = { "nome": "Outros", "porcentagem": Decimal("0") }
                        lista["irmas"].append(outros)

                    outros["porcentagem"] += categoria["porcentagem"]

                if "filhos" in categoria:
                    montar_listas(categoria["nome"], categoria["filhos"], listas)

        listas = []
        montar_listas("Raiz", arvore, listas)

        output = u""

        for lista in listas:
            try:
                figure = pyplot.figure(figsize=(6, 6))
                ax = figure.add_subplot(111)
                labels = [c["nome"] for c in lista["irmas"]]
                fracs = [c["porcentagem"] for c in lista["irmas"]]
                ax.pie(fracs, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.set_title(lista["mae"])

                img_file, img_path = mkstemp(suffix=".png")
                img_url = path2url(img_path)
                figure.savefig(img_path, format="png")
                output += u"<img src=\"{img_url}\" />\n".format(img_url=img_url)
            finally:
                pyplot.close(figure)

        return output



class DespesasPorCategoriaReportTable(Table2):
    """
    Tabela pro relatório de despesas agrupadas por categoria.

    """

    title = "Tabela"

    fields = (
        TableField2("Categoria"),
        TableField2("Total", classes=["currency"]),
        TableField2("Porcentagem das despesas", classes=["percentage"]),
        TableField2("Porcentagem das vendas", classes=["percentage"]),
    )

    @property
    def body(self):
        despesas = list(DespesaDeCaixa.objects.filter(dia__in=self.data)) + \
                list(MovimentacaoBancaria.objects.filter(dia__in=self.data, valor__lt=0))

        self._total_despesas = Decimal(sum(d.valor for d in despesas))

        if not self._total_despesas:
            return []

        vendas = Venda.objects.filter(dia__in=self.data)
        total_vendas = Decimal(sum(v.conta for v in vendas))

        categoria_dict_dict = {}

        # Acumula despesas com `categoria == None`
        outros = {
            "total": Decimal("0"),
        }

        for despesa in despesas:
            if despesa.categoria:
                caminho_categorias = [despesa.categoria] + despesa.categoria.ascendentes

                for categoria in caminho_categorias:
                    categoria_dict = categoria_dict_dict.setdefault(categoria.slug, {
                            "total": Decimal("0"),
                            "outros": {
                                "total": Decimal("0"),
                            },
                    })

                    categoria_dict["total"] += despesa.valor

                categoria_dict = categoria_dict_dict[categoria.slug]

                # Se a categoria tem filhos, a despesa deve ser categorizada como
                # "Outros".
                #
                # Ex: se há "Fornecedor > Vinhos" e a despesa está como
                # "Fornecedor", deve ser listada como "Fornecedor > Outros"

                if despesa.categoria.filhas.count():
                    categoria_dict["outros"]["total"] += despesa.valor
            else:
                logger.debug(u"Despesa sem categoria: {0}".format(despesa))
                outros["total"] += despesa.valor


        logger.debug(u"Total de despesas sem categoria: {0}".format(len([d for d in despesas if not d.categoria])))


        # Calcula porcentagem em relação à despesa total
        for categoria_dict in categoria_dict_dict.values():
            razao_das_despesas = abs(categoria_dict["total"] / self._total_despesas)
            razao_das_vendas = abs(categoria_dict["total"] / total_vendas)

            categoria_dict["porcentagem_das_despesas"] = "{:.2%}".format(razao_das_despesas)
            categoria_dict["porcentagem_das_vendas"] = "{:.2%}".format(razao_das_vendas)

            if categoria_dict["outros"]["total"]:
                razao_das_despesas = abs(categoria_dict["outros"]["total"] / self._total_despesas)
                razao_das_vendas = abs(categoria_dict["outros"]["total"] / total_vendas)

                categoria_dict["outros"]["porcentagem_das_despesas"] = "{:.2%}".format(razao_das_despesas)
                categoria_dict["outros"]["porcentagem_das_vendas"] = "{:.2%}".format(razao_das_vendas)


        razao_das_despesas_outros = abs(outros["total"] / self._total_despesas)
        razao_das_vendas_outros = abs(outros["total"] / total_vendas)

        outros["porcentagem_das_despesas"] = "{:.2%}".format(razao_das_despesas_outros)
        outros["porcentagem_das_vendas"] = "{:.2%}".format(razao_das_vendas_outros)


        categoria_tuple_list = []
        for slug, categoria_dict in categoria_dict_dict.items():
            categoria = CategoriaDeMovimentacao.objects.get(slug=slug)

            if categoria.filhas.count():
                nome = u"{0} - Total".format(categoria.nome_completo)
            else:
                nome = categoria.nome_completo

            categoria_tuple_list.append((
                nome,
                format_currency(categoria_dict["total"]),
                categoria_dict["porcentagem_das_despesas"],
                categoria_dict["porcentagem_das_vendas"],
            ))

            if categoria_dict["outros"]["total"]:
                categoria_tuple_list.append((
                    categoria.SEPARADOR.join([categoria.nome_completo, "Outros"]),
                    format_currency(categoria_dict["outros"]["total"]),
                    categoria_dict["outros"]["porcentagem_das_despesas"],
                    categoria_dict["outros"]["porcentagem_das_vendas"],
                ))

        if outros["total"]:
            categoria_tuple_list.append((
                u"Outros",
                format_currency(outros["total"]),
                outros["porcentagem_das_despesas"],
                outros["porcentagem_das_vendas"],
            ))

        return sorted(categoria_tuple_list, key=lambda r: r[0]) # Ordena por nome completo da categoria

    @property
    def footer(self):
        return [("TOTAL", self._total_despesas, "100%", "-")]


class DespesasPorCategoriaReport(Report2):
    """
    Relatório de meses.

    Elementos:

        - Graficos de torta de totais de despesas por categorias
        - Tabela de despesas por categoria

    """
    title="Relatório de despesas por categoria"
    # FIXME: gráficos de torta estão saindo errados
    #element_classes = [DespesasPorCategoriaCharts, DespesasPorCategoriaReportTable]
    element_classes = [DespesasPorCategoriaReportTable]

class DespesasPorCategoriaReportView(ReportView):
    """
    Class-based view do relatório de despesas por categoria. Filtra os
    dias por data de início e data de fim.

    """

    Report = DespesasPorCategoriaReport
    FilterForm = DateFilterForm2

    def get_raw_data(self):
        return Dia.objects.all()

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


    relatorio_meses_form = IntervaloMesesFilterForm()

    relatorio_simples_form = RelatorioSimplesForm({'de': inicio_do_mes.strftime("%d/%m/%Y"),
                                                   'ateh': hoje.strftime("%d/%m/%Y"), })
    ano_filter_form = AnoFilterForm(initial={"ano": hoje.strftime("%Y")}, datefield_name="data")
    date_filter_form = DateFilterForm(initial={
                                        "from_date": inicio_do_mes.strftime("%d/%m/%Y"),
                                        "to_date": hoje.strftime("%d/%m/%Y"),
                                      }, datefield_name="data")
    date_filter_form2 = DateFilterForm2(initial={
                                        "from_date": inicio_do_mes.strftime("%d/%m/%Y"),
                                        "to_date": hoje.strftime("%d/%m/%Y"),
                                      }, datefield_name="data")


    return render_to_response('relatorios/index.html', {
                                'title': "Relatórios",
                                'relatorio_simples_form': relatorio_simples_form,
                                'relatorio_meses_form': relatorio_meses_form,
                                'ano_filter_form': ano_filter_form,
                                'date_filter_form': date_filter_form,
                                'date_filter_form2': date_filter_form2,
                                  'voltar_link': '/',
                                  'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))
