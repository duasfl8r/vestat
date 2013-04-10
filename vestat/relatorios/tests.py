# -*- encoding: utf-8 -*-

"""
Testes da app `relatorios`
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from vestat.caixa.models import Dia
from views import AnualReportTable

class RelatorioAnualTestCase(TestCase):
    """
    Testes do Relatório Anual
    """

    fixtures = ["testes_2012-contabil", "testes_2012-caixa"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("vestat.relatorios.views.anual")

    def teste_carrega_ano_com_dias_abertos(self):
        response = self.client.get(self.url, {"ano": 2012})
        self.assertEqual(response.status_code, 200)

    def teste_carrega_ano_sem_dias_abertos(self):
        response = self.client.get(self.url, {"ano": 2013})
        self.assertEqual(response.status_code, 200)


class AnualReportTableTestCase(TestCase):
    fixtures = ["testes_2012-contabil", "testes_2012-caixa"]

    def teste_ano_todo(self):
        data = Dia.objects.filter(data__year=2012)
        table = AnualReportTable(data)

        self.assertTrue(len(table.body))
