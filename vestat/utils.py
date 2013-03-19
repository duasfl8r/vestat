# -*- encoding: utf-8 -*-
import os, errno

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
