# -*- encoding: utf-8 -*-

class Link():
    def __init__(self, slug, name, url, description=None):
        self.slug = slug
        self.name = name
        self.url = url
        self.description = description if description else ""

    def __hash__(self):
        return hash(self.slug)


class Page():
    def __init__(self, name):
        self.name = name
        self._configurations = {}
        self._default = {}

    def add(self, link, group_name=None):
        if group_name:
            group = self._configurations.setdefault(group_name, {})
        else:
            group = self._default

        group[link.slug] = link

    def groups(self):
        group_tuples = [("", self._default)] + self._configurations.items()

        return [
            { "name": n, "links": l.values() }
            for n, l in group_tuples
        ]

config_pages = {
    "vestat": Page("Configurações")
}
