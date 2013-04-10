# -*- encoding: utf-8 -*-

from django.template import Context, loader
from django.template.defaultfilters import slugify

from core import ReportElement

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
