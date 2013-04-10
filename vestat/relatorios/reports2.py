# -*- encoding: utf-8 -*-

"""
Novas classes de relatórios e seus elementos.
"""

from django.template import Context, loader, TemplateDoesNotExist
from django.template.defaultfilters import slugify

class Report2():
    """
    Classe abstrata pra um relatório.

    Subclasses devem sobrecrever os atributos `title` e
    `element_classes`.

    """

    title = "Subclass me!"
    """
    Título do relatório
    """

    element_classes = []
    """
    Classes dos elementos que compõem o relatório -- tabelas, gráficos, etc.

    Cada uma dessas classes deve ser uma subclasse de `ReportElement`.
    """

    def __init__(self, data):
        """
        Inicializa o relatório: cria seus elementos alimentando as
        classes em `element_classes` com os dados fornecidos.

        Argumentos:

            - data: os dados sob os quais o relatório fala.
        """
        self.data = data
        self.elements = [Element(data) for Element in self.element_classes]

    def render(self, format):
        """
        Retorna o conteúdo do relatório no formato especificado.
        Elementos que não suportam esse formato não serão exibidos.

        Argumentos:

            - format: uma string contendo o formato desejado
            (i.e.  "html", "csv").
        """

        template_name = "report2.{0}".format(format)

        try:
            template = loader.get_template(template_name)
        except TemplateDoesNotExist:
            return None
        else:
            context = Context({
                "report": self,
            })
            return template.render(context)

class ReportElement():
    """
    Classe abstrata para elementos de um relatório -- tabelas, gráficos etc.

    Subclasses devem implementar os métodos render_{formato} nos
    formatos aceitos por elas (i.e. render_html, render_csv).

    Esses métodos devem retornar o conteúdo no formato correto pra ser incluído
    no relatório de mesmo formato -- `render_html` deve retornar uma string
    em HTML, `render_csv` uma string no formato CSV etc.
    """

    def __init__(self, data):
        """
        Inicializa o elemento, guardando os dados fornecidos.

        Argumentos:

            - data: os dados sob os quais o elemento fala.
        """
        self.data = data


class TableField2():
    """
    Um campo (uma coluna) de uma tabela.
    """

    def __init__(self, header, slug=None, classes=[]):
        """
        Inicializa o objeto, armazenando os argumentos fornecidos.

        Argumentos:
            - header: o título da coluna
            - slug: um slug pro título
            - classes: classes CSS a serem usadas ao renderizar a tabela
              em HTML
        """

        self.header = header
        self.slug = slug or slugify(header)
        self.classes = classes


class Table2(ReportElement):
    """
    Classe abstrata pra uma tabela.

    Subclasses devem sobrescrever os atributos `title` e `fields`, e
    implementar a property `body`.
    """

    title = ""
    """
    Título da tabela
    """

    fields = []
    """
    Objetos `TableField2` representando as colunas da tabela.
    """

    @property
    def body(self):
        """
        Retorna uma lista de listas, cada uma representando uma linha do
        corpo da tabela, na ordem a serem exibidas.
        """
        pass

    def render(self, format):
        """
        Encapsula a renderização de diversos formatos na mesma função.

        Usa um template com extensão igual ao formato desejado.

        Argumentos:

            - format: o formato de renderização
        """

        template_name = "elements/table.{0}".format(format)
        template = loader.get_template(template_name)
        context = Context({
            "title": self.title,
            "fields": self.fields,
            "body": self.body,
        })
        return template.render(context)

    def render_html(self):
        """
        Renderiza o template em HTML.
        """
        return self.render("html")

    def render_csv(self):
        """
        Renderiza o template em CSV.
        """
        return self.render("csv")
