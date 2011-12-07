# -*- encoding: utf8 -*-
import datetime
import random

from django.test import TestCase
from django.db.models import Sum, Count

from models import Dia, Venda, secs_to_time


def random_date(year=None, month=None, day=None):
    """Returns a random `datetime.date` object, with fixed `year`,
    `month` or `day`."""

    year = year or random.randint(2008, 2011)
    month = month or random.randint(1, 12)
    day = day or random.randint(1, 31)

    while True:
        try:
            return datetime.date(year, month, day)
        except ValueError:
            day -= 1

class PermanenciaTestCase(TestCase):
    def setUp(self):
        data = datetime.date.today()
        self.dia = Dia(data=data, feriado=False, anotacoes="")
        self.dia.save()

    def dummy_venda(self, hora_entrada, hora_saida):
        venda = Venda(dia=self.dia, mesa="10", hora_entrada=hora_entrada,
                      hora_saida=hora_saida, categoria="L")
        venda.fechada = True
        venda.save()
        return venda

    def test_secs_to_time(self):
        time1 = datetime.time(20, 00)
        time2 = datetime.time(00, 00)
        time3 = datetime.time(00, 01)
        time4 = datetime.time(23, 59, 59)

        self.assertEqual(secs_to_time(72000), time1)
        self.assertEqual(secs_to_time(0), time2)
        self.assertEqual(secs_to_time(60), time3)
        self.assertEqual(secs_to_time(86399), time4)

    def test_calcular_permanencia_ate_meia_noite(self):
        hora_entrada = datetime.time(21, 0)
        hora_saida = datetime.time(0, 0)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(venda.calcular_permanencia(hora_entrada, hora_saida),
                         3600 * 3)

    def test_permanencia_mesmo_dia(self):
        hora_entrada = datetime.time(20, 00)
        hora_saida = datetime.time(23, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         datetime.time(03, 00))

    def test_permanencia_outro_dia(self):
        hora_entrada = datetime.time(20, 00)
        hora_saida = datetime.time(01, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         datetime.time(05, 00))

    def test_permanencia_ate_meia_noite(self):
        hora_entrada = datetime.time(20, 00)
        hora_saida = datetime.time(00, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         datetime.time(4, 00))

    def test_permanencia_media(self):
        horass = ((datetime.time(19, 00), datetime.time(23, 00)), # 4
                 (datetime.time(22, 30), datetime.time(23, 30)), # 1
                 (datetime.time(19, 00), datetime.time(02, 00))) # 7

        for horas in horass:
            self.dummy_venda(*horas)

        self.assertEqual(self.dia.permanencia_media(), datetime.time(04, 00))


class PermanenciaTotalTestCase(TestCase):
    def dummy_dia(self, data):
        dia = Dia(data=data, feriado=False, anotacoes="")
        dia.save()
        return dia

    def dummy_venda(self, dia, hora_entrada, hora_saida):
        venda = Venda(dia=dia, mesa="10", hora_entrada=hora_entrada,
                      hora_saida=hora_saida, categoria="L")
        venda.fechada = True
        venda.save()
        return venda

    def setUp(self):
        dias = { datetime.date(2011, 1, 1): ((datetime.time(23, 0),
                                                datetime.time(1, 0)), # 2

                                               (datetime.time(22, 0),
                                                datetime.time(3, 0)), # 5

                                               (datetime.time(20, 0),
                                                datetime.time(23, 0))), # 3
                                               # total: 10

                  datetime.date(2011, 1, 2): ((datetime.time(23, 0),
                                                datetime.time(2, 0)), # 3

                                               (datetime.time(21, 0),
                                                datetime.time(1, 0)), # 4

                                               (datetime.time(20, 0),
                                                datetime.time(1, 0))), # 5
                                               # total: 12


                  datetime.date(2011, 1, 3): ((datetime.time(23, 0),
                                                datetime.time(0, 0)), # 1

                                               (datetime.time(20, 0),
                                                datetime.time(21, 0))), # 1
                                               # total: 2
               } # total: 24, media: 8

        for data in dias:
            dia = self.dummy_dia(data)
            for horas in dias[data]:
                self.dummy_venda(dia, horas[0], horas[1])

    def test_permanencia_media_total(self):
        self.assertEqual(Dia.permanencia_media_total(), datetime.time(3))


class DiaTestCase(TestCase):
    def test_categoria_semanal_semana(self):
        dias = [ ((2011, 11, 23), "semana"),
                 ((2011, 11, 25), "sexta"),
                 ((2011, 11, 26), "sabado"),
                 ((2011, 11, 27), "domingo"),
        ]

        for data, resultado in dias:
            dia = Dia(data=datetime.datetime(*data))
            self.assertEqual(dia.categoria_semanal(), resultado)

        dia_feriado = Dia(feriado=True)
        self.assertEqual(dia_feriado.categoria_semanal(), 'feriado')

    
