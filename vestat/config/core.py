# -*- encoding: utf-8 -*-

class Link():
    def __init__(self, name, url, description=None):
        self.name = name
        self.url = url
        self.description = description if description else ""


class Page():
    def __init__(self, name):
        self.name = name
        self._configurations = {}
        self._default = []

    def add(self, link, group_name=None):
        if group_name:
            group = self._configurations.setdefault(group_name, [])
        else:
            group = self._default

        group.append(link)

    def groups(self):
        group_tuples = [("Gerais", self._default)] + self._configurations.items()

        return [
            { "name": n, "links": l }
            for n, l in group_tuples
        ]

config_pages = {
    "vestat": Page("Configurações do vestat")
}

