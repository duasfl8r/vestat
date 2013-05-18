# -*- encoding: utf-8 -*-
"""
Cria páginas de configurações que podem ser construídas por outras
aplicações.

Como usar esse módulo
=====================

Criando uma página de configuração
----------------------------------

>>> from config import config_pages, Page
>>> config_pages["especiais"] = Page("Configurações especiais")


Adicionando links a uma página de configuração criada
-----------------------------------------------------

>>> from config import config_pages, Link
>>> config_pages["especiais"].add(
        Link(
            u"sensibilidade-autogestor",
            u"Sensibilidade do autogestor acoplado",
            u"/autogestor/sensibilidade/",
            u"Altera a sensibilidade do autogestor acoplado, fazendo com " \
            "que ele transfira os mapeamentos referenciados com uma " \
            "tolerância maior ou menor"
        )
    )

Acessando uma página de configurações
-------------------------------------

Para acessar a página de configurações armazenada em
`config_pages["especiais"]`, acesse:

    /config/especiais/

(assumindo que a aplicação `config` está mapeada pra `/config/` no
`urls.py` do projeto)

"""

class Link():
    """
    Um link de uma página de configurações.
    """

    def __init__(self, slug, name, url, description=None):
        """
        Inicializa o objeto `Link`.

        Argumentos:

            - slug: string; um rótulo pro link contendo somente
              letras, números e hífens; deve ser único dentro de um
              grupo de uma página; usado pra armazená-lo internamente.

            - name: string; o nome que aparecerá na página de
              configurações.

            - url: string; a URL pra qual o link apontará.

            - description: string ou `None`: uma descrição opcional que
              aparece ao lado do link; se não for passada, não será
              exibida descrição.
        """

        self.slug = slug
        self.name = name
        self.url = url
        self.description = description if description else ""

    def __hash__(self):
        return hash(self.slug)


class Page():
    """
    Uma página de configuração.

    Possui diversos *grupos*, incluindo um grupo "padrão". Cada grupo
    armazena objetos `Link`.

    Esses grupos servem pra, ahm, *agrupar* os links semanticamente.

    """

    def __init__(self, name):
        """
        Inicializa o objeto `Link`, criando um grupo padrão vazio.

        Argumentos:
            - name: o nome da página, usado como título quando ela for
              exibida.
        """
        self.name = name
        self._configurations = {}
        self._default = {}

    def add(self, link, group_name=None):
        """
        Adiciona um link a um grupo página.

        Caso o grupo fornecido ainda não exista, será criado.

        Caso não seja fornecido um grupo, o link será adicionado no
        grupo padrão.

        Argumentos:
            - link: objeto `Link`
            - group_name: string ou `None`; o nome do grupo.
        """

        if group_name:
            group = self._configurations.setdefault(group_name, {})
        else:
            group = self._default

        group[link.slug] = link

    def groups(self):
        """
        Retorna uma lista de dicionários, cada um representando um dos
        grupos da página.

        Cada dicionário tem duas chaves: 'name' é o nome/título, e
        'links' é uma lista de objetos `Link` correspondentes aos links
        do grupo.

        O primeiro grupo é o padrão, e o valor armazenado em 'name' é
        uma string vazia.
        """

        group_tuples = [("", self._default)] + self._configurations.items()

        return [
            { "name": n, "links": l.values() }
            for n, l in group_tuples
        ]

config_pages = {
    "vestat": Page("Configurações"),
}
"""
Dicionário que armazena as páginas de configuração criadas.

As chaves desse dicionário são os *slugs* usados pra acessá-los pela
URL, e os valores são objetos `Page`.

Já é criada uma página de configurações, 'vestat'.

"""
