# -*- encoding: utf8 -*-
from datetime import date, time, datetime, timedelta
import random
from decimal import Decimal
from fractions import Fraction

from django.test import TestCase
from django.db.models import Sum, Count
from django.conf import settings
from django.test.client import Client

from models import Dia, Venda, DespesaDeCaixa, \
    secs_to_time, PagamentoComCartao, Bandeira, CategoriaDeMovimentacao, \
    SLUG_CATEGORIA_GORJETA

from vestat.django_utils import format_currency
from vestat.config.models import VestatConfiguration
from vestat.contabil.models import Registro, Transacao, Lancamento

from caixa import NOME_DO_REGISTRO


def random_date(year=None, month=None, day=None):
    """Returns a random `date` object, with fixed `year`,
    `month` or `day`."""

    year = year or random.randint(2008, 2011)
    month = month or random.randint(1, 12)
    day = day or random.randint(1, 31)

    while True:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1

class PermanenciaTestCase(TestCase):
    def setUp(self):
        data = date.today()
        self.dia = Dia(data=data, anotacoes="")
        self.dia.save()

    def dummy_venda(self, hora_entrada, hora_saida):
        venda = Venda(dia=self.dia, mesa="10", hora_entrada=hora_entrada,
                      hora_saida=hora_saida, categoria="L")
        venda.fechada = True
        venda.save()
        return venda

    def test_secs_to_time(self):
        time1 = time(20, 00)
        time2 = time(00, 00)
        time3 = time(00, 01)
        time4 = time(23, 59, 59)

        self.assertEqual(secs_to_time(72000), time1)
        self.assertEqual(secs_to_time(0), time2)
        self.assertEqual(secs_to_time(60), time3)
        self.assertEqual(secs_to_time(86399), time4)

    def test_calcular_permanencia_ate_meia_noite(self):
        hora_entrada = time(21, 0)
        hora_saida = time(0, 0)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(venda.calcular_permanencia(hora_entrada, hora_saida),
                         3600 * 3)

    def test_permanencia_mesmo_dia(self):
        hora_entrada = time(20, 00)
        hora_saida = time(23, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         time(03, 00))

    def test_permanencia_outro_dia(self):
        hora_entrada = time(20, 00)
        hora_saida = time(01, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         time(05, 00))

    def test_permanencia_ate_meia_noite(self):
        hora_entrada = time(20, 00)
        hora_saida = time(00, 00)
        venda = self.dummy_venda(hora_entrada, hora_saida)

        self.assertEqual(secs_to_time(venda.permanencia),
                         time(4, 00))

    def test_permanencia_media(self):
        horass = ((time(19, 00), time(23, 00)), # 4
                 (time(22, 30), time(23, 30)), # 1
                 (time(19, 00), time(02, 00))) # 7

        for horas in horass:
            self.dummy_venda(*horas)

        self.assertEqual(self.dia.permanencia_media(), time(04, 00))


class PermanenciaTotalTestCase(TestCase):
    def dummy_dia(self, data):
        dia = Dia(data=data, anotacoes="")
        dia.save()
        return dia

    def dummy_venda(self, dia, hora_entrada, hora_saida):
        venda = Venda(dia=dia, mesa="10", hora_entrada=hora_entrada,
                      hora_saida=hora_saida, categoria="L")
        venda.fechada = True
        venda.save()
        return venda

    def setUp(self):
        dias = { date(2011, 1, 1): ((time(23, 0),
                                                time(1, 0)), # 2

                                               (time(22, 0),
                                                time(3, 0)), # 5

                                               (time(20, 0),
                                                time(23, 0))), # 3
                                               # total: 10

                  date(2011, 1, 2): ((time(23, 0),
                                                time(2, 0)), # 3

                                               (time(21, 0),
                                                time(1, 0)), # 4

                                               (time(20, 0),
                                                time(1, 0))), # 5
                                               # total: 12


                  date(2011, 1, 3): ((time(23, 0),
                                                time(0, 0)), # 1

                                               (time(20, 0),
                                                time(21, 0))), # 1
                                               # total: 2
               } # total: 24, media: 8

        for data in dias:
            dia = self.dummy_dia(data)
            for horas in dias[data]:
                self.dummy_venda(dia, horas[0], horas[1])

    def test_permanencia_media_total(self):
        self.assertEqual(Dia.permanencia_media_total(), time(3))


class DiaTestCase(TestCase):
    def test_categoria_semanal_semana(self):
        dias = [ ((2011, 11, 23), "semana"),
                 ((2011, 11, 25), "sexta"),
                 ((2011, 11, 26), "sabado"),
                 ((2011, 11, 27), "domingo"),
        ]

        for data, resultado in dias:
            dia = Dia(data=datetime(*data))
            self.assertEqual(dia.categoria_semanal(), resultado)

class VendaTestCase(TestCase):
    def setUp(self):
        self.dia = Dia(data=datetime(2012, 02, 14))
        self.dia.save()

    def test_choices(self):
        for cat in [c[0] for c in Venda.CATEGORIA_CHOICES]:
            for cid in [c[0] for c in Venda.CIDADE_CHOICES]:
                pousadas_flat = sum([c[1] for c in Venda.POUSADA_CHOICES], [])
                for pou in [p[0] for p in pousadas_flat]:
                    venda = Venda(dia=self.dia,
                                  mesa="1",
                                  hora_entrada=time(20, 00),
                                  hora_saida=time(22, 00),
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


class TestCaseVestatBoilerplate(TestCase):
    """
    Um TestCase que cria os objetos `contabil.models.Registro` e
    `config.models.VestatConfiguration` usados na aplicação.
    """

    def setUp(self):
        self.config = VestatConfiguration()
        self.config.save()

        self.registro = Registro(nome=NOME_DO_REGISTRO)
        self.registro.save()

class CaixaSemDiaDeTrabalhoTestCase(TestCaseVestatBoilerplate):
    def setUp(self):
        super(CaixaSemDiaDeTrabalhoTestCase, self).setUp()

        self.c = Client()
        self.response = self.c.get("/caixa/", follow=True)

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_sem_dia_de_trabalho(self):
        self.assertTrue("dia" not in self.response.context)

class CaixaDiaDeTrabalhoZeradoTestCase(TestCaseVestatBoilerplate):
    def setUp(self):
        super(CaixaDiaDeTrabalhoZeradoTestCase, self).setUp()

        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.response = self.c.get(self.url_hoje + "criar", follow=True)

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_tem_dia(self):
        self.assertTrue("dia" in self.response.context)

    def test_remover_dia(self):
        response = self.c.get(self.url_hoje + "remover", follow=True)
        self.assertTrue("dia" not in response.context)

class CaixaAdicionarVendaFormTestCase(TestCaseVestatBoilerplate):
    def setUp(self):
        super(CaixaAdicionarVendaFormTestCase, self).setUp()

        self.c = Client()
        self.url_hoje = "/caixa/2011/12/07/"
        self.c.get(self.url_hoje + "criar", follow=True)

    def test_retornou_200(self):
        response = self.c.get(self.url_hoje + "venda/adicionar")
        self.assertEqual(response.status_code, 200)

class CaixaAdicionarVendaTestCase(TestCaseVestatBoilerplate):
    def setUp(self):
        super(CaixaAdicionarVendaTestCase, self).setUp()

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
        self.assertEqual(self.venda.hora_entrada, time(*hora_entrada))
        self.assertEqual(self.venda.num_pessoas, self.data["num_pessoas"])
        self.assertEqual(self.venda.categoria, self.data["categoria"])
        self.assertEqual(self.venda.cidade_de_origem, self.data["cidade_de_origem"])
        self.assertEqual(self.venda.pousada_que_indicou, self.data["pousada_que_indicou"])



class CaixaFecharVendaSemCartaoTestCase(TestCaseVestatBoilerplate):
    fixtures = ['cartoes_teste.json']

    def setUp(self):
        super(CaixaFecharVendaSemCartaoTestCase, self).setUp()

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
                "conta": format_currency(190.00),
                "gorjeta": format_currency(19.00),
                "pgto_dinheiro": format_currency(100),
                "pgto_cheque": format_currency(90),
        }

        self.response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_fechar, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_fechou_venda(self):
        self.assertEqual(self.venda.fechada, True)

    def test_dados_conferem(self):
        self.assertEqual(format_currency(self.venda.conta), self.data_fechar["conta"])
        hora_saida = map(int, self.data_fechar["hora_saida"].split(":"))
        self.assertEqual(self.venda.hora_saida, time(*hora_saida))
        self.assertEqual(format_currency(self.venda.gorjeta), self.data_fechar["gorjeta"])
        self.assertEqual(format_currency(self.venda.pgto_dinheiro), self.data_fechar["pgto_dinheiro"])
        self.assertEqual(format_currency(self.venda.pgto_cheque), self.data_fechar["pgto_cheque"])
        self.assertEqual(list(self.venda.pagamentocomcartao_set.all()), [])

class CaixaFecharVendaComCartaoTestCase(TestCaseVestatBoilerplate):
    fixtures = ['cartoes_teste.json']

    def setUp(self):
        super(CaixaFecharVendaComCartaoTestCase, self).setUp()

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
                "valor": "60",
        }
        response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_cartao, follow=True)

        self.data_fechar = {
                "fechar_venda": "Fechar venda",
                "hora_saida": "00:30",
                "conta": format_currency(190.00),
                "gorjeta": format_currency(19.00),
                "pgto_dinheiro": format_currency(100),
                "pgto_cheque": format_currency(30),
        }

        self.response = self.c.post(self.venda.get_absolute_url() + "saida", self.data_fechar, follow=True)
        self.venda = response.context["dia"].venda_set.all()[0]

    def test_retornou_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_fechou_venda(self):
        self.assertEqual(self.venda.fechada, True)

    def test_dados_conferem(self):
        self.assertEqual(format_currency(self.venda.conta), self.data_fechar["conta"])
        hora_saida = map(int, self.data_fechar["hora_saida"].split(":"))
        self.assertEqual(self.venda.hora_saida, time(*hora_saida))
        self.assertEqual(format_currency(self.venda.gorjeta), self.data_fechar["gorjeta"])
        self.assertEqual(format_currency(self.venda.pgto_dinheiro), self.data_fechar["pgto_dinheiro"])
        self.assertEqual(format_currency(self.venda.pgto_cheque), self.data_fechar["pgto_cheque"])
        self.assertEqual(len(self.venda.pagamentocomcartao_set.all()), 1)
        self.assertEqual(self.venda.pagamentocomcartao_set.all()[0].valor, Decimal(self.data_cartao["valor"]))
        self.assertEqual(self.venda.pagamentocomcartao_set.all()[0].bandeira.id, self.data_cartao["bandeira"])


class DiaDezPorcentoTestCase(TestCaseVestatBoilerplate):
    """
    Testes do cálculo de 10% e de seus processos subjacentes.

    """

    def setUp(self):
        """
        Cria os objetos necessários pra calcular os 10% a pagar:

        - Objeto `caixa.models.Dia`
        - Objeto `caixa.models.Venda`

        """

        super(DiaDezPorcentoTestCase, self).setUp()

        self.dia = Dia(data=datetime(2012, 02, 14))
        self.dia.save()

        self.venda = Venda(dia=self.dia,
                      mesa="1",
                      hora_entrada=time(20, 00),
                      hora_saida=time(22, 00),
                      num_pessoas=10,
                      conta=Decimal("200"),
                      gorjeta=Decimal("20"),
                      categoria="L",
                      cidade_de_origem="Rio de Janeiro",
                      pousada_que_indicou="Amarylis",
                      pgto_dinheiro=Decimal("200"),
        )
        self.venda.save()

    def test_criar_venda_nao_cria_transacao_10p(self):
        self.assertEqual(len(self.registro.transacoes.all()), 0)

    def test_fechar_venda_cria_transacao_10p(self):
        self.venda.fechar()

        self.assertEqual(len(self.registro.transacoes.all()), 1)

        transacao = self.registro.transacoes.all()[0]

    def test_reabrir_venda_remove_transacao_10p(self):
        self.venda.fechar()
        self.venda.abrir()
        self.assertEqual(len(self.registro.transacoes.all()), 0)

    def test_remover_venda_remove_transacao_10p(self):
        self.venda.delete()
        self.assertEqual(len(self.registro.transacoes.all()), 0)

    def test_fechar_venda_fechada_nao_cria_transacao_10p(self):
        self.venda.fechar()
        self.venda.fechar()
        self.assertEqual(len(self.registro.transacoes.all()), 1)

    def test_abrir_venda_aberta_nao_remove_transacao_10p(self):
        self.venda.abrir()
        self.assertEqual(len(self.registro.transacoes.all()), 0)


class DiaDezPorcentoAPagarTestCase(TestCaseVestatBoilerplate):
    """
    Teste do cálculo do valor de 10% a pagar.
    """

    fixtures = ["categorias_de_movimentacao_teste"]

    def setUp(self):
        super(DiaDezPorcentoAPagarTestCase, self).setUp()

        self.dia = Dia(data=datetime(2012, 02, 14))
        self.dia.save()

    def teste_10p_a_pagar_zerado(self):
        self.assertEqual(self.dia.dez_porcento_a_pagar(), Decimal("0"))

    def abre_venda_200_reais(self):
        self.venda = Venda(dia=self.dia,
                      mesa="1",
                      hora_entrada=time(20, 00),
                      hora_saida=time(22, 00),
                      num_pessoas=10,
                      conta=Decimal("200"),
                      gorjeta=Decimal("20"),
                      categoria="L",
                      cidade_de_origem="Rio de Janeiro",
                      pousada_que_indicou="Amarylis",
                      pgto_dinheiro=Decimal("200"),
        )
        self.venda.save()

    def teste_abre_venda_e_10p_a_pagar_continua_zerado(self):
        self.abre_venda_200_reais()
        self.assertEqual(self.dia.dez_porcento_a_pagar(), Decimal("0"))


    def teste_fecha_venda_e_10p_a_pagar_aumenta_certo(self):
        self.abre_venda_200_reais()
        self.venda.fechar()

        fracao_aumento_da_divida = Fraction.from_decimal(Decimal("20")) * \
                Fraction(9, 10) *  \
                self.config.fracao_10p_funcionarios
        dezp_a_pagar = self.dia.dez_porcento_a_pagar()

        self.assertEqual(dezp_a_pagar, Decimal(float(fracao_aumento_da_divida)))

    def adiciona_despesa_de_10p(self):
        categoria_10p = CategoriaDeMovimentacao.objects.get(slug=SLUG_CATEGORIA_GORJETA)
        self.despesa = DespesaDeCaixa(dia=self.dia,
                categoria=categoria_10p,
                valor=Decimal("-10"))
        self.despesa.save()


    def teste_adiciona_despesa_e_10p_a_pagar_diminui_certo(self):
        self.adiciona_despesa_de_10p()

        self.assertEqual(self.dia.dez_porcento_a_pagar(), Decimal("-10"))


    def teste_adiciona_venda_e_despesa_e_10p_a_pagar_fica_certo(self):
        self.abre_venda_200_reais()
        self.venda.fechar()

        fracao_aumento_da_divida = Fraction.from_decimal(Decimal("20")) * \
                Fraction(9, 10) *  \
                self.config.fracao_10p_funcionarios
        dezp_a_pagar = self.dia.dez_porcento_a_pagar()


        self.adiciona_despesa_de_10p()
        dezp_a_pagar -= Decimal("10")
        self.assertEqual(self.dia.dez_porcento_a_pagar(), dezp_a_pagar)


class PagamentoComCartaoTestCase(TestCaseVestatBoilerplate):
    fixtures = ["feriados_bancarios", "categorias_de_movimentacao_teste"]

    def setUp(self):
        super(PagamentoComCartaoTestCase, self).setUp()

        self.bandeira_debito = Bandeira(
            nome="Bandeira 1",
            categoria="D",
            contagem_de_dias="U",
            prazo_de_deposito=2,
            taxa=Decimal("0.02")
        )
        self.bandeira_debito.save()

        self.bandeira_credito = Bandeira(
            nome="Bandeira 2",
            categoria="C",
            contagem_de_dias="C",
            prazo_de_deposito=31,
            taxa=Decimal("0.033"),
        )
        self.bandeira_credito.save()

    def dummy_pgto(self, data, bandeira, valor):
        dia = Dia(data=data)
        dia.save()

        venda = Venda(
            dia=dia,
            mesa="1",
            hora_entrada=time(20, 00),
            hora_saida=time(22, 00),
            num_pessoas=10,
            conta=valor,
            gorjeta=Decimal("20"),
            categoria="L",
        )
        venda.save()

        pgto = PagamentoComCartao(
            valor=valor,
            bandeira=bandeira,
            venda=venda,
        )
        pgto.save()

        venda.fechar()

        return pgto

    def teste_dias_uteis_durante_semana(self):
        bandeira = self.bandeira_debito # 2 dias úteis
        data_pgto = date(2013, 4, 1) # segunda-feira, sem feriados
        data_prevista = date(2013, 4, 3)

        pgto = self.dummy_pgto(data_pgto, bandeira, Decimal("200"))
        self.assertEqual(pgto.data_do_deposito, data_prevista)

    def teste_dias_uteis_com_fds(self):
        bandeira = self.bandeira_debito # 2 dias úteis
        data_pgto = date(2013, 4, 5) # sexta-feira, sem feriados
        data_prevista = date(2013, 4, 9)

        pgto = self.dummy_pgto(data_pgto, bandeira, Decimal("200"))
        self.assertEqual(pgto.data_do_deposito, data_prevista)

    def teste_dias_uteis_com_fds_e_feriado(self):
        bandeira = self.bandeira_debito # 2 dias úteis
        data_pgto = date(2012, 11, 1) # quinta-feira, Finados na sexta
        data_prevista = date(2012, 11, 6)

        pgto = self.dummy_pgto(data_pgto, bandeira, Decimal("200"))
        self.assertEqual(pgto.data_do_deposito, data_prevista)

    def teste_dias_corridos(self):
        bandeira = self.bandeira_credito # 2 dias úteis
        intervalo = timedelta(31)

        datas_teste = [
            date(2012, 1, 1),
            date(2012, 5, 1),
            date(2012, 3, 15),
            date(2012, 12, 31),
        ]

        for data in datas_teste:
            data_pgto = data
            data_prevista = data + intervalo

            pgto = self.dummy_pgto(data_pgto, bandeira, Decimal("200"))
            self.assertEqual(pgto.data_do_deposito, data_prevista)
