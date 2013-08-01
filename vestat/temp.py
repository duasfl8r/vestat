# -*- encoding: utf-8 -*-

"""
Funções pra criar e remover arquivos temporários que precisem ser
visíveis via HTTP -- imagens, por exemplo.
"""

import os
import logging
import tempfile
from datetime import datetime, timedelta

from django.conf import settings

IGNORE_FILES = ["README.txt"]

logger = logging.getLogger(__name__)

def mkstemp(*args, **kwargs):
    """
    Wrapper pro `tempfile.mkstemp` pra criar arquivos dentro do
    diretório de mídia do django.

    Atua exatamente como o `mkstemp` original, exceto que configura
    o kwarg "dir" pro diretório definido em `settings.MEDIA_ROOT`.

    Se for passado um outro kwarg "dir" pra essa função, usa ele em vez
    disso.

    """

    if "dir" not in kwargs:
        kwargs["dir"] = os.path.join(settings.MEDIA_ROOT, "tmp")

    return tempfile.mkstemp(*args, **kwargs)

def path2url(path):
    """
    Retorna a URL pra acessar um arquivo do diretório de mídia a partir
    do seu caminho como arquivo.

    """

    return u"{media}tmp/{basename}".format(
        media=settings.MEDIA_URL,
        basename=os.path.split(path)[-1],
    )


def clear(older_than=86400):
    """
    Limpa os arquivos temporários antigos.

    Argumentos:

        - older_than: intervalo após o qual um arquivo temporário será
          deletado, após ser criado/modificado, em segundos.

    """

    interval = timedelta(seconds=older_than)
    now = datetime.now()
    logger.debug("Limpando arquivos temporários antigos -- older_than={0}".format(older_than))
    tmp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")

    for dir_path, _, basenames in os.walk(tmp_dir, topdown=False):
        for basename in basenames:
            filename = os.path.join(dir_path, basename)

            if os.path.relpath(filename, start=tmp_dir) in IGNORE_FILES:
                logger.debug("Pulando {filename}...")
                continue

            msg = "Analisando {0}...".format(filename)
            mtime = datetime.fromtimestamp(os.stat(filename).st_mtime)
            if now - mtime > interval:
                msg += " ANTIGO, sendo removido..."
                os.remove(filename)
            logger.debug(msg)
