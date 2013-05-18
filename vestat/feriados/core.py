# -*- encoding: utf-8 -*-
from itertools import groupby

from vestat.utils import daterange_inclusive

from feriados.models import Feriado

def eh_feriado(data):
    """
    Retorna `True` se houver um feriado cadastrado na data fornecida, e
    `False` se não houver.

    Argumentos:
        - data: um objeto `datetime.date`.
    """

    for feriado in Feriado.objects.all():
        if feriado.acontece_em(data):
            return True
    return False

def eh_dia_util(data):
    """
    Retorna `True` se a data for um dia de semana e se não houver um
    feriado cadastrado nessa data, e `False` se a data for um final de
    semana ou se houver um feriado cadastrado nessa data.

    Argumentos:
        - data: um objeto `datetime.date`.
    """

    return data.weekday() in range(0, 5) and not(eh_feriado(data))

def feriados_entre(d1, d2):
    """
    Retorna uma lista de tuplas com os feriados entre duas datas,
    *inclusive*. As tuplas possuem o formato `(date, feriado)`, onde:

    - `date` é o objeto `datetime.date` do dia do feriado
    - `Feriado` é o objeto `Feriado` correspondente.

    Argumentos:
        - d1: objeto `datetime.date`, a data de início da busca.
        - d2: objeto `datetime.date`, a data de fim da busca.
    """

    datas = daterange_inclusive(d1, d2)
    datas_agrupadas_por_ano = groupby(datas, lambda d: d.year)

    for ano, datas in datas_agrupadas_por_ano:
        datas_feriados = {(f.data_em(ano), f) for f in Feriado.objects.all()}
        for data_teste in datas:
            for data_feriado, feriado in datas_feriados:
                if data_feriado == data_teste:
                    yield (data_feriado, feriado)
