# -*- encoding: utf-8 -*-
import os.path
import shutil
import sys
import argparse

import settings
from django.core.management import setup_environ
setup_environ(settings)
from django.conf import settings

DIRETORIO_DE_INSTALACAO = "C:\\vestat"

DJANGO_APP_DIRS = [app[7:] for app in settings.INSTALLED_APPS if app.startswith("vestat")]

ARQUIVOS = ({
        "origem": DJANGO_APP_DIRS + ["media", "templates", "manage.py",
            "middleware.py", "settings.py", "urls.py", "views.py",
            "context_processors.py", "utils.py", "__init__.py"],

        "destino": "vestat"
     },
     {
         "origem": [os.path.join("trecos", "iniciar_servidor.bat"), os.path.join("trecos", "vestat.py")],
         "destino": ""
     }
)

print("Instalando {0} em {1}...".format(settings.NOME_APLICACAO, DIRETORIO_DE_INSTALACAO))

parser = argparse.ArgumentParser(description="Instalar o {0}".format(settings.NOME_APLICACAO))
parser.add_argument("-v, --verbose", help="Exibe informações adicionais", dest="verbose", action="store_true")
args = parser.parse_args()

if os.path.exists(DIRETORIO_DE_INSTALACAO):
    shutil.rmtree(DIRETORIO_DE_INSTALACAO)
else:
    if args.verbose:
        print("Diretório {0} não existe; criando...".format(DIRETORIO_DE_INSTALACAO))
    os.mkdir(DIRETORIO_DE_INSTALACAO)

for copia in ARQUIVOS:
    origem, destino = copia["origem"], copia["destino"]

    for arq in origem:
        DESTINO = os.path.join(DIRETORIO_DE_INSTALACAO, destino, os.path.basename(arq))
        if args.verbose:
            print("Copiando {0} para {1}...".format(arq, destino))
        if os.path.isdir(arq):
            shutil.copytree(arq, DESTINO)
        elif os.path.isfile(arq):
            shutil.copy(arq, DESTINO)
        else:
            print("ATENÇÃO: Arquivo/diretório não existe: {0}".format(arq))
