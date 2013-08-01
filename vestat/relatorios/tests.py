# -*- encoding: utf-8 -*-

"""
Testes da app `relatorios`
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from vestat.caixa.models import Dia
from views import MesesReportTable

class MesesReportTestCase(TestCase):
    """
    Testes do relatório de meses
    """

    fixtures = ["testes_2012-contabil", "testes_2012-caixa"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("relatorio_meses")

    def teste_carrega_ano_com_dias_abertos(self):
        response = self.client.get(self.url,
            {"from_date_year": 2012, "from_date_month": 1, "to_date_year": 2012, "to_date_month": 12})
        self.assertEqual(response.status_code, 200)

    def teste_carrega_ano_sem_dias_abertos(self):
        response = self.client.get(self.url,
            {"from_date_year": 2013, "from_date_month": 1, "to_date_year": 2013, "to_date_month": 12})
        self.assertEqual(response.status_code, 200)


class MesesReportTableTestCase(TestCase):
    fixtures = ["testes_2012-contabil", "testes_2012-caixa"]

    def teste_ano_todo(self):
        data = Dia.objects.filter(data__year=2012)
        table = MesesReportTable(data)

        self.assertTrue(len(table.body))
