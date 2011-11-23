# -*- encoding: utf-8 -*-
import os.path
import shutil
import sys

import settings
from django.core.management import setup_environ
setup_environ(settings)
from django.conf import settings

DIRETORIO_DE_INSTALACAO = "C:\\vestat"
ARQUIVOS = (
            (["caixa", "config", "media", "relatorios", "templates", "manage.py",
              "middleware.py", "settings.py", "urls.py", "views.py", "__init__.py"],
              "vestat"),
            
            (["etc\\Python27", "trecos\\iniciar_servidor.bat",
              "trecos\\vestat.py"], "")
            )

if os.path.exists(DIRETORIO_DE_INSTALACAO):
    ANTIGO = DIRETORIO_DE_INSTALACAO + ".antigo"
    shutil.rmtree(ANTIGO, ignore_errors=True)
    shutil.move(DIRETORIO_DE_INSTALACAO, ANTIGO)

os.mkdir(DIRETORIO_DE_INSTALACAO)

for arquivos, destino in ARQUIVOS:
    for arq in arquivos:
        DESTINO = os.path.join(DIRETORIO_DE_INSTALACAO, destino, os.path.basename(arq))
        if "-v" in sys.argv:
            print "Copiando:", DESTINO
        if os.path.isdir(arq):
            shutil.copytree(arq, DESTINO)
        elif os.path.isfile(arq):
            shutil.copy(arq, DESTINO)
        else:
            print "Não existe:", arq
