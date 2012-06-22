# -*- encoding: utf8 -*-
import datetime
import random
from decimal import Decimal

from django.test import TestCase
from django.db.models import Sum, Count
from django.conf import settings
from django.test.client import Client

from models import Dia, Venda, DespesaDeCaixa, MovimentacaoBancaria, secs_to_time
from vestat.config.models import VestatConfiguration


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

class VendaTestCase(TestCase):
    def setUp(self):
        self.dia = Dia(data=datetime.datetime(2012, 02, 14))
        self.dia.save()

    def test_choices(self):
        for cat in [c[0] for c in Venda.CATEGORIA_CHOICES]:
            for cid in [c[0] for c in Venda.CIDADE_CHOICES]:
                pousadas_flat = sum([c[1] for c in Venda.POUSADA_CHOICES], [])
                for pou in [p[0] for p in pousadas_flat]:
                    venda = Venda(dia=self.dia,
                                  mesa="1",
                                  hora_entrada=datetime.time(20, 00),
                                  hora_saida=datetime.time(22, 00),
                                  num_pessoas=10,
                                  conta=Decimal("200"),
                                  gorjeta=Decimal("20"),
                                  categoria=cat,
                                  cidade_de_origem=cid,
                                  pousada_que_indicou=pou,
                                  pgto_dinheiro=Decimal("200"),
                    )
                    venda.fechada = True
                    venda.save()

class DespesaTestCase(TestCase):
    def setUp(self):
        self.dia = Dia(data=datetime.datetime(2012, 02, 14))
        self.dia.save()

    def test_choices(self):
        for cat in [c[0] for c in DespesaDeCaixa.CATEGORIA_CHOICES]:
            print("Categoria: {cat}".format(**vars()))
            despesa = DespesaDeCaixa(dia=self.dia,
                              valor=Decimal("100.0"),
                              categoria=cat,
                              descricao="teste!")
            despesa.save()



class CaixaSemDiaDeTrabalhoTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.response = self.c.get("/caixa/", follow=True)

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_sem_dia_de_trabalho(self):
        self.assertTrue("dia" not in self.response.context)

class CaixaDiaDeTrabalhoZeradoTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.response = self.c.get(self.url_hoje + "criar", follow=True)

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_tem_dia(self):
        self.assertTrue("dia" in self.response.context)

    def test_dia_vazio_caixa_0(self):
        self.assertEqual(self.response.context["dia"].caixa_de_hoje(), 0)

    def test_gorjeta_inicial_1142(self):
        self.assertEqual(self.response.context["dia"].gorjeta_descontada_de_hoje(), 1142.0)

    def test_nao_eh_feriado(self):
        self.assertEqual(self.response.context["dia"].feriado, False)

    def test_virar_feriado(self):
        response = self.c.post(self.url_hoje, { "feriado": True })
        self.assertEqual(response.context["dia"].feriado, True)

    def test_remover_dia(self):
        response = self.c.get(self.url_hoje + "remover", follow=True)
        self.assertTrue("dia" not in response.context)

class CaixaAdicionarVendaFormTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.c.get(self.url_hoje + "criar", follow=True)

    def test_retornou_200(self):
        response = self.c.get(self.url_hoje + "venda/adicionar")
        self.assertEqual(response.status_code, 200)

class CaixaAdicionarVendaTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.c.get(self.url_hoje + "criar", follow=True)

        self.data = {
            "mesa": "1",
            "hora_entrada": "23:00",
            "num_pessoas": 5,
            "categoria": "T",
            "cidade_de_origem": "Rio de Janeiro",
            "pousada_que_indicou": "Amarylis",
        }
        self.response = self.c.post(self.url_hoje + "venda/adicionar", self.data, follow=True)
        self.venda = self.response.context["dia"].venda_set.all()[0]

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_adicionou_venda(self):
        self.assertEqual(len(self.response.context["dia"].venda_set.all()), 1)

    def test_dados_conferem(self):
        self.assertEqual(self.venda.mesa, self.data["mesa"])
        hora_entrada = map(int, self.data["hora_entrada"].split(":"))
        self.assertEqual(self.venda.hora_entrada, datetime.time(*hora_entrada))
        self.assertEqual(self.venda.num_pessoas, self.data["num_pessoas"])
        self.assertEqual(self.venda.categoria, self.data["categoria"])
        self.assertEqual(self.venda.cidade_de_origem, self.data["cidade_de_origem"])
        self.assertEqual(self.venda.pousada_que_indicou, self.data["pousada_que_indicou"])



class CaixaFecharVendaSemCartaoTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.c.get(self.url_hoje + "criar", follow=True)

        self.data_abrir = {
            "mesa": "1",
            "hora_entrada": "23:00",
            "num_pessoas": 5,
            "categoria": "T",
            "cidade_de_origem": "Rio de Janeiro",
            "pousada_que_indicou": "Amarylis",
        }
        response = self.c.post(self.url_hoje + "venda/adicionar", self.data_abrir, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

        self.data_fechar = {
                "fechar_venda": "Fechar venda",
                "hora_saida": "00:30",
                "conta": "190.00",
                "gorjeta": "19.00",
                "pgto_dinheiro": "100",
                "pgto_cheque": "90",
        }

        self.response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_fechar, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_fechou_venda(self):
        self.assertEqual(self.venda.fechada, True)

    def test_dados_conferem(self):
        self.assertEqual(self.venda.conta, Decimal(self.data_fechar["conta"]))
        hora_saida = map(int, self.data_fechar["hora_saida"].split(":"))
        self.assertEqual(self.venda.hora_saida, datetime.time(*hora_saida))
        self.assertEqual(self.venda.gorjeta, Decimal(self.data_fechar["gorjeta"]))
        self.assertEqual(self.venda.pgto_dinheiro, Decimal(self.data_fechar["pgto_dinheiro"]))
        self.assertEqual(self.venda.pgto_cheque, Decimal(self.data_fechar["pgto_cheque"]))
        self.assertEqual(list(self.venda.pagamentocomcartao_set.all()), [])

class CaixaFecharVendaComCartaoTestCase(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.c.get(self.url_hoje + "criar", follow=True)

        self.data_abrir = {
            "mesa": "1",
            "hora_entrada": "23:00",
            "num_pessoas": 5,
            "categoria": "T",
            "cidade_de_origem": "Rio de Janeiro",
            "pousada_que_indicou": "Amarylis",
        }
        response = self.c.post(self.url_hoje + "venda/adicionar", self.data_abrir, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

        self.data_cartao = {
                "adicionar_pgto_cartao": "Adicionar",
                "bandeira": 1,
                "categoria": "D",
                "valor": "60",
        }
        response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_cartao, follow=True)

        self.data_fechar = {
                "fechar_venda": "Fechar venda",
                "hora_saida": "00:30",
                "conta": "190.00",
                "gorjeta": "19.00",
                "pgto_dinheiro": "100",
                "pgto_cheque": "30",
        }

        self.response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_fechar, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_fechou_venda(self):
        self.assertEqual(self.venda.fechada, True)

    def test_dados_conferem(self):
        self.assertEqual(self.venda.conta, Decimal(self.data_fechar["conta"]))
        hora_saida = map(int, self.data_fechar["hora_saida"].split(":"))
        self.assertEqual(self.venda.hora_saida, datetime.time(*hora_saida))
        self.assertEqual(self.venda.gorjeta, Decimal(self.data_fechar["gorjeta"]))
        self.assertEqual(self.venda.pgto_dinheiro, Decimal(self.data_fechar["pgto_dinheiro"]))
        self.assertEqual(self.venda.pgto_cheque, Decimal(self.data_fechar["pgto_cheque"]))
        self.assertEqual(len(self.venda.pagamentocomcartao_set.all()), 1)
        self.assertEqual(self.venda.pagamentocomcartao_set.all()[0].valor, Decimal(self.data_cartao["valor"]))
        self.assertEqual(self.venda.pagamentocomcartao_set.all()[0].categoria, self.data_cartao["categoria"])
        self.assertEqual(self.venda.pagamentocomcartao_set.all()[0].bandeira.id, self.data_cartao["bandeira"])



class DiaGorjetaTestCase(TestCase):
    def setUp(self):
        VestatConfiguration().save()

    def test_saldo_inicial_zerado(self):
        dia = Dia(data=datetime.datetime.now())
        self.assertEqual(dia.gorjeta_descontada_total(), Decimal('0'))

    def test_novo_saldo_inicial(self):
        config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
        config.saldo_inicial_gorjetas = Decimal('1000')
        config.save()
        dia = Dia(data=datetime.datetime.now())
        self.assertEqual(dia.gorjeta_descontada_total(), Decimal('1000'))

    def test_inserindo_gorjeta_fechando(self):
        config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
        config.saldo_inicial_gorjetas = Decimal('1000')
        config.save()

        dia = Dia(data=datetime.datetime.now())
        dia.save()

        venda = Venda(dia=dia,
                      mesa="1",
                      hora_entrada=datetime.time(20, 00),
                      hora_saida=datetime.time(22, 00),
                      num_pessoas=10,
                      conta=Decimal("200"),
                      gorjeta=Decimal("20"),
                      categoria='L',
                      cidade_de_origem="Rio de Janeiro",
                      pousada_que_indicou="Amarylis",
                      pgto_dinheiro=Decimal("200"),
        )
        venda.fechada = True
        venda.save()

        self.assertEqual(
            dia.gorjeta_descontada_total(),
            Decimal('1000') + \
            (Decimal('20') * Decimal('0.9') * Decimal('2') / Decimal('3'))
        )

    def test_inserindo_gorjeta_sem_fechar(self):
        config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
        config.saldo_inicial_gorjetas = Decimal('1000')
        config.save()

        dia = Dia(data=datetime.datetime.now())
        dia.save()

        venda = Venda(dia=dia,
                      mesa="1",
                      hora_entrada=datetime.time(20, 00),
                      hora_saida=datetime.time(22, 00),
                      num_pessoas=10,
                      conta=Decimal("200"),
                      gorjeta=Decimal("20"),
                      categoria='L',
                      cidade_de_origem="Rio de Janeiro",
                      pousada_que_indicou="Amarylis",
                      pgto_dinheiro=Decimal("200"),
        )
        venda.fechada = False
        venda.save()

        self.assertEqual(dia.gorjeta_descontada_total(), Decimal('1000'))

    def test_descontando_gorjeta_fechando(self):
        config = VestatConfiguration.objects.get(pk=settings.ID_CONFIG)
        config.saldo_inicial_gorjetas = Decimal('1000')
        config.save()

        dia = Dia(data=datetime.datetime.now())
        dia.save()

        despesa = DespesaDeCaixa(dia=dia, categoria='G', valor=Decimal('-100'))
        despesa.save()

        movbancaria = MovimentacaoBancaria(dia=dia, categoria='G', valor=Decimal('-100'))
        movbancaria.save()

        self.assertEqual(dia.gorjeta_descontada_total(), Decimal('800'))
