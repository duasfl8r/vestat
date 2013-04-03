# -*- encoding: utf-8 -*-
import logging

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from vestat.django_utils import format_currency, format_date
from vestat.calendario import Event
from models import PagamentoComCartao
from views import ver_dia

logger = logging.getLogger("vestat")

def daterange_inclusive(d1, d2):
    from datetime import timedelta
    while d1 <= d2:
        yield d1
        d1 += timedelta(1)

def dia_events(begin, end):
    for d in daterange_inclusive(begin, end):
        kwargs = {
            "ano": "{0:04d}".format(d.year),
            "mes": "{0:02d}".format(d.month),
            "dia": "{0:02d}".format(d.day),
        }

        link = reverse(ver_dia, kwargs=kwargs)
        nome = u'<a href="{link}">Caixa</a>'.format(link=link)

        yield Event(d, mark_safe(nome))

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
