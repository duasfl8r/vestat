# -*- encoding: utf-8 -*-
import os, errno
from datetime import timedelta

"""
Classes e funções utilitárias que NÃO dependem do Django.
"""

def mkdir_p(path):
    """
    Cria o diretório fornecido (e seus pais, se necessário) caso ele não exista.  (imita `mkdir -p`)
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def daterange_inclusive(d1, d2):
    """
    Retorna uma iterator com todos os objetos `datetime.date` entre duas datas.

    Argumentos:
        - d1: um objeto `datetime.date`
        - d2: um objeto `datetime.date`
    """
    while d1 <= d2:
        yield d1
        d1 += timedelta(1)
