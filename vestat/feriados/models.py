# -*- encoding: utf-8 -*-
"""
Modelos da aplicação 'feriados'.
"""

from datetime import date, timedelta
from dateutil import easter

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from vestat.config import config_pages, Link
from django.core.urlresolvers import reverse_lazy

class Feriado(models.Model):
    """
    Um feriado de data única, anual fixa ou anual móvel.

    Feriados de data única são representados por um objeto `datetime.date`.

    Feriados de data anual fixa são representados por uma string no formato "DD/MM".

    Feriados de data anual móvel são representados por uma expressão
    python que calcula o feriado em um determinado ano, dados os seguintes valores:

    - `pascoa` é o objeto `datetime.date` correspondente à Páscoa desse
      ano.

    - `d` é uma função que recebe um inteiro e representa um certo
      número de dias.

    Dessa maneira, pra calcular um feriado que acontece 60 dias após a
    Páscoa, o campo de data anual móvel deve conter:

        pascoa + d(60)
    """

    nome = models.CharField(u"Nome do feriado", max_length=250, blank=False, null=False)
    data_unica = models.DateField(u"Data única", null=True, blank=True)
    data_anual_fixa = models.CharField(u"Data anual fixa", max_length=5, null=True, blank=True, help_text=u"Formato: DD/MM")
    data_anual_movel = models.CharField(u"Data móvel", null=True, blank=True, max_length=100,
            help_text=u"Uma expressão aritmética, com 'pascoa' significando o dia da páscoa "
                      u"e 'd' sendo a função timedelta.")

    class Meta:
        ordering = ["-data_unica", "-data_anual_fixa"]


    _campos_de_data = ["data_unica", "data_anual_fixa", "data_anual_movel"]


    def __unicode__(self):
        return self.nome

    def _data_anual_movel_em(self, ano):
        """
        Retorna a data anual móvel no ano fornecido.

        Assume que o feriado é anual móvel.

        Esse método deve ser usado internamente.

        Argumentos:
            - ano: um inteiro; o ano consultado.
        """
        return eval(self.data_anual_movel, {
            "pascoa": easter.easter(ano),
            "d": timedelta,
        })

    def clean(self, *args, **kwargs):
        """
        Valida os campos do objeto `Feriado`.

        Verifica se um e apenas um dos campos de data foi preenchido.

        Se o campo `data_anual_movel` foi preenchido, verifica se sua
        execução não dá erros e retorna um objeto `datetime.date`.
        """

        super(Feriado, self).clean(*args, **kwargs)

        if self.data_anual_movel:
            try:
                resultado = self._data_anual_movel_em(2012)

                if not isinstance(resultado, date):
                    raise ValidationError(u"'data_anual_movel' não retorna uma data")
            except Exception:
                import traceback
                raise ValidationError(u"Campo 'data_anual_movel' em formato inválido: {0}" \
                        .format(traceback.format_exc(1).decode("utf-8")))

        campos_de_data_preenchidos = filter(bool, [getattr(self, campo) for campo in Feriado._campos_de_data])

        def quoted_verbose_name(field_name):
            verbose_name = Feriado._meta.get_field(field_name).verbose_name
            return u'"{0}"'.format(verbose_name)

        if len(campos_de_data_preenchidos) != 1:
            raise ValidationError(u"Deve-se preencher um (e apenas um) dos campos {campos}" \
                .format(campos=u", ".join(quoted_verbose_name(nome_campo) for nome_campo in Feriado._campos_de_data)))


    @property
    def data(self):
        """
        Uma descrição da data do feriado, de acordo com o tipo escolhido.
        """

        if self.data_unica:
            return self.data_unica.strftime(settings.SHORT_DATE_FORMAT_PYTHON)
        elif self.data_anual_fixa:
            return "Anual fixa: {0}".format(self.data_anual_fixa)
        else:
            return "Anual móvel: `{0}`".format(self.data_anual_movel)

    def data_em(self, ano):
        """
        A data em que o feriado cai no ano fornecido.

        Argumentos:
            - ano: um inteiro; o ano consultado.
        """

        if self.data_unica and self.data_unica.year == ano:
            return self.data_unica
        elif self.data_anual_fixa:
            dia, mes = [int(p, 10) for p in self.data_anual_fixa.split("/")]
            return date(ano, mes, dia)
        elif self.data_anual_movel:
            return self._data_anual_movel_em(ano)
        else:
            return None

    def acontece_em(self, data):
        """
        Retorna `True` se o feriado acontece na data fornecida, e
        `False` se não acontece.

        Argumentos:
            - data: objeto `datetime.date`; a data consultada.
        """

        ano = data.year

        return data == self.data_em(ano)

config_pages["vestat"].add(
    Link(
        "feriados",
        "Feriados",
        reverse_lazy("admin:feriados_feriado_changelist"),
        "Adicionar/remover/editar"
    ),
)
"""
Link na página de configurações: editar os feriados no Django Admin
Site.
"""
