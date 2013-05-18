# -*- encoding: utf-8 -*-
"""
Novo sistema de relatórios do Vestat.

"""

from django.template import Context, loader, TemplateDoesNotExist
from django.template.defaultfilters import slugify

class Report2():
    """
    Classe abstrata pra um relatório.

    Um relatório possui vários *elementos*, construídos a partir do
    atributo de classe `Report2.element_classes`.

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
