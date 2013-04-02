# -*- encoding: utf-8 -*-
import logging

from vestat.django_utils import format_currency, format_date
from vestat.calendario import Event
from models import PagamentoComCartao

logger = logging.getLogger("vestat")

def dias_de_deposito_events(begin, end):
    pagamentos = PagamentoComCartao.objects.filter(data_do_deposito__range=(begin, end))

    dias = {}
    for p in pagamentos:
        dias.setdefault(p.data_do_deposito, []).append(p)

    for data, pagamentos in dias.items():

        valor_total = sum((p.valor - p.taxa) for p in pagamentos)
        nome = u"Entrada dos cartões: R$ {0}".format(format_currency(valor_total))

        descricao = "\n".join(
            u"R$ ({pgto} - {taxa}), {bandeira}, {data}".format(
                bandeira = p.bandeira,
                pgto = format_currency(p.valor),
                taxa = format_currency(p.taxa),
                data = format_date(p.venda.dia.data))
            for p in pagamentos)

        yield Event(data, nome, descricao)
