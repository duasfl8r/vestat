# -*- encoding: utf-8 -*-
from __future__ import print_function
import os.path
import shutil
import sys
import argparse
import platform

import vestat.settings as settings

if platform.system() == "Windows":
    DIRETORIO_DE_INSTALACAO = "C:\\vestat"
elif platform.system() == "Linux":
    DIRETORIO_DE_INSTALACAO = "/opt/vestat/"
else:
    print("Plataforma não suportada")
    exit(-1)

ARQUIVOS = (
     {
         "origem": ["vestat"],
         "destino": ""
     },
     {
         "origem": [os.path.join("trecos", "iniciar_servidor.bat")],
         "destino": ""
     }
)

print("Instalando {0} em {1}...".format(settings.NOME_APLICACAO, DIRETORIO_DE_INSTALACAO))

parser = argparse.ArgumentParser(description="Instalar o {0}".format(settings.NOME_APLICACAO))
parser.add_argument("-v, --verbose", help="Exibe informações adicionais", dest="verbose", action="store_true")
args = parser.parse_args()

if os.path.exists(DIRETORIO_DE_INSTALACAO):
    opt = ""

    while opt.lower() not in ["s", "n"]:
        print("Diretório {0} existe; remover?".format(DIRETORIO_DE_INSTALACAO), end=" ")
        opt = raw_input("[s/n] ")

    if opt == "s":
        shutil.rmtree(DIRETORIO_DE_INSTALACAO)
    else:
        print("Instalação cancelada")
        exit(0)
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
