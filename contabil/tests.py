# -*- encoding: utf-8 -*-
import datetime
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from contabil import join
from contabil.models import Registro, Transacao, Lancamento

class RegistroTestCase(TestCase):
    def setUp(self):
        self.registro = Registro(nome="Registro teste")
        self.registro.save()

    def test_balanco_inicial_zero(self):
        self.assertEqual(self.registro.balanco(join("gastos", "funcionarios")), Decimal("0"))

    def test_transacao_faz_novo_balanco(self):
        transacao = Transacao(
                registro=self.registro,
                data=datetime.date.today(),
                descricao="Transação de teste"
        )

        transacao.save()

        transacao.lancamentos.create(
            conta=join("gastos", "funcionarios"),
            valor=Decimal("100.00"),
        )

        transacao.lancamentos.create(
            conta=join("bens", "caixa"),
            valor=Decimal("-100.00"),
        )

        self.assertEqual(self.registro.balanco(join("gastos", "funcionarios")), Decimal("100"))
        self.assertEqual(self.registro.balanco(join("bens", "caixa")), Decimal("-100"))

    def test_transacao_com_soma_zero_eh_consistente(self):
        transacao = Transacao(
                registro=self.registro,
                data=datetime.date.today(),
                descricao="Transação de teste"
        )

        transacao.save()

        transacao.lancamentos.create(
            conta=join("gastos", "funcionarios"),
            valor=Decimal("100.00"),
        )

        transacao.lancamentos.create(
            conta=join("bens", "caixa"),
            valor=Decimal("-100.00"),
        )

        self.assertTrue(transacao.eh_consistente)

    def test_transacao_com_soma_nao_zero_nao_eh_consistente(self):
        transacao = Transacao(
                registro=self.registro,
                data=datetime.date.today(),
                descricao="Transação de teste"
        )

        transacao.save()

        transacao.lancamentos.create(
            conta=join("gastos", "funcionarios"),
            valor=Decimal("100.00"),
        )

        transacao.lancamentos.create(
            conta=join("bens", "caixa"),
            valor=Decimal("-99.00"),
        )

        self.assertFalse(transacao.eh_consistente)


class LancamentoTestCase(TestCase):
    def setUp(self):
        self.registro = Registro(nome="Registro teste")
        self.registro.save()

        self.transacao = Transacao(
                registro=self.registro,
                data=datetime.date.today(),
                descricao="Transação de teste"
        )
        self.transacao.save()

    def test_lancamento_sem_conta_dah_erro(self):
        lancamento = Lancamento(transacao=self.transacao, valor=Decimal("10.00"))
        self.assertRaises(ValidationError, lambda: lancamento.save())

