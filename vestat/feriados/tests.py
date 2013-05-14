# -*- encoding: utf-8 -*-
from datetime import date
from dateutil import easter

from django.test import TestCase
from django.core.exceptions import ValidationError

from feriados.models import Feriado
from core import eh_feriado, feriados_entre

def tenta_clean(instance):
    return lambda: instance.clean()


class ArgumentosInsuficientesTestCase(TestCase):
    def teste_sem_nada(self):
        f = Feriado()
        self.assertRaises(ValidationError, lambda: f.full_clean())

    def teste_sem_data(self):
        f = Feriado(nome=u"Dia dos trabalhadores")
        self.assertRaises(ValidationError, lambda: f.full_clean())

    def teste_duas_datas(self):
        f = Feriado(nome=u"Dia dos trabalhadores", data_anual_fixa="01/05", data_unica=date(2013, 5, 1))
        self.assertRaises(ValidationError, lambda: f.full_clean())

    def teste_sem_nome(self):
        f = Feriado(data_anual_fixa="01/05")
        self.assertRaises(ValidationError, lambda: f.full_clean())

    def teste_sem_nome2(self):
        f = Feriado(data_anual_movel="pascoa + d(3)")
        self.assertRaises(ValidationError, lambda: f.full_clean())


class DataUnicaTestCase(TestCase):
    def teste_com_mesmo_ano(self):
        f = Feriado(nome=u"Dia dos trabalhadores de 2013", data_unica=date(2013, 5, 1))
        f.save()
        self.assertEqual(f.data_em(2013), date(2013, 5, 1))

    def teste_com_ano_diferente(self):
        f = Feriado(nome=u"Dia dos trabalhadores de 2013", data_unica=date(2013, 5, 1))
        f.save()
        self.assertEqual(f.data_em(2012), None)


class DataAnualFixaTestCase(TestCase):
    def teste_DD_MM(self):
        f = Feriado(nome=u"Dia dos trabalhadores", data_anual_fixa="01/05")
        f.save()
        self.assertEqual(f.data_em(2013), date(2013, 5, 1))

    def teste_D_M(self):
        f = Feriado(nome=u"Dia dos trabalhadores", data_anual_fixa="1/5")
        f.save()
        self.assertEqual(f.data_em(2013), date(2013, 5, 1))


class DataAnualMovelTestCase(TestCase):
    def teste_pascoa_1990_a_2030(self):
        f = Feriado(nome=u"Páscoa", data_anual_movel="pascoa")
        for ano in range(1990, 2030):
            self.assertEqual(f.data_em(ano), easter.easter(ano))

    def teste_carnaval_2013(self):
        terca_carnaval_2013 = date(2013, 2, 12)

        feriado = Feriado(nome=u"Terça de carnaval",
            data_anual_movel="pascoa - d(47)")

        self.assertEqual(feriado.data_em(2013), terca_carnaval_2013)


class DataAnualMovelEvalInconsistenteTestCase(TestCase):
    def teste_pascoa_escrito_errado(self):
        feriado = Feriado(nome=u"Teste", data_anual_movel="pascao - d(47)") # 'pascao'
        self.assertRaises(ValidationError, tenta_clean(feriado))

    def teste_falta_parenteses(self):
        feriado = Feriado(nome=u"Teste", data_anual_movel="pascoa - d(47")
        self.assertRaises(ValidationError, tenta_clean(feriado))

    def teste_usa_inteiros_como_dias(self):
        feriado = Feriado(nome=u"Teste", data_anual_movel="pascoa - 47")
        self.assertRaises(ValidationError, tenta_clean(feriado))

    def teste_nao_retorna_uma_data(self):
        feriado = Feriado(nome=u"Teste", data_anual_movel="18")
        self.assertRaises(ValidationError, tenta_clean(feriado))

    def teste_vazio(self):
        feriado = Feriado(nome=u"Teste", data_anual_movel="")
        self.assertRaises(ValidationError, tenta_clean(feriado))


class FeriadosBancarios2012TestCase(TestCase):
    fixtures = ["feriados_bancarios.json"]

    def setUp(self):
        # Feriados de 2012
        # Fonte: http://calendario.retira.com.br/feriados/brasil/2012/

        self.feriados_teste = (
            date(2012, 1, 1),   # Ano novo
            date(2012, 2, 20),  # Carnaval
            date(2012, 2, 21),  # Carnaval
            date(2012, 4, 8),   # Páscoa
            date(2012, 4, 21),  # Tiradentes
            date(2012, 5, 1),   # Dia do trabalho
            date(2012, 6, 7),   # Corpus Christi
            date(2012, 9, 7),   # Independência do Brasil
            date(2012, 10, 12), # Nossa Senhora Aparecida
            date(2012, 11, 2),  # Finados
            date(2012, 11, 15),  # Proclamação da República
            date(2012, 12, 25), # Natal
        )

    def teste_checar_feriados(self):
        for deve_ser_feriado in self.feriados_teste:
            if not eh_feriado(deve_ser_feriado):
                self.fail("{0} deve ser feriado!".format(deve_ser_feriado))


class FeriadosEntreTestCase(TestCase):
    fixtures = ["feriados_bancarios.json"]

    def teste_exclusive(self):
        d1 = date(2011, 12, 31)
        d2 = date(2012, 2, 22)

        self.assertEqual(len(list(feriados_entre(d1, d2))), 3)
        # ano novo, carnaval, carnaval

    def teste_inclusive(self):
        d1 = date(2012, 1, 1)
        d2 = date(2012, 2, 21)

        self.assertEqual(len(list(feriados_entre(d1, d2))), 3)
        # ano novo, carnaval, carnaval
