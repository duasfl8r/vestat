# -*- encoding: utf-8 -*-
"""
Comando 'atualizar', opera mudanças de banco de dados necessárias pra
atualizações do Vestat.
"""
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from vestat.config.management.converter_dump import converter
from vestat.django_utils import criar_superusuario

def sync_and_evolve():
    """
    Roda os comandos 'syncdb' e 'evolve' do django management, de forma
    não-interativa.
    """

    # Sincroniza o banco de dados
    call_command('syncdb', interactive=False)

    # Evolui o banco de dados com o Django Evolution
    call_command('evolve', interactive=False, execute=True, hint=True, database="default")


def versao_1_2_2(cmd, *args):
    """
    Atualizações pra versão 1.2.2.

    Deve ser chamada após exportar o banco de dados pra um arquivo de
    dump JSON e remover o arquivo do banco de dados.

    Ações:

    - Cria um novo banco de dados e o superusuário padrão
    - Faz as conversões necessárias sobre o dump nos modelos que mudaram
    - Importa o dump convertido pro banco de dados
    - Carrega fixture de feriados bancários

    Argumentos da linha de comando:
        - dump_file: arquivo de dump do banco de dados na versão
          1.2.1
    """
    if len(args) != 1:
        raise CommandError("Uso: atualizar 1.2.2 <dump_file>\n\ndump: arquivo de dump do banco de dados anterior (JSON)")

    sync_and_evolve()
    criar_superusuario()

    print("Convertendo entradas no modelo antigo pro novo modelo...")

    novo_bd_json = converter(args[0])
    tmp_dump_filename = "fixture_convertida.json"

    print("Armazenando dados convertidos em {tmp_dump_filename}".format(**vars()))

    with open(tmp_dump_filename, "w") as tmp_dump_file:
        tmp_dump_file.write(novo_bd_json)

    print("Carregando dados convertidos no banco de dados...")

    call_command("loaddata", tmp_dump_filename)

    print("Removendo arquivo temporário...")
    os.remove(tmp_dump_filename)

    print("Carregando fixture de feriados bancários...")
    call_command("loaddata", "feriados_bancarios")

    print("Reunindo arquivos estáticos...")
    call_command("collectstatic", interactive=False)

def versao_1_2_0(cmd, *args):
    sync_and_evolve()
    criar_superusuario()


class Command(BaseCommand):
    args = '<versao>'
    help = 'Faz as modificações necessárias para uma determinada versão'

    def handle(self, *args, **options):
        versoes_disponiveis = { nome.replace("versao_", "").replace("_", "."): item for nome, item in globals().items() if nome.startswith("versao_") }
        nomes_das_versoes = [ nome for nome, _ in versoes_disponiveis.items() ]

        if len(args) < 1:
            raise CommandError("Uso: atualizar " + self.args + " [ARG...]\n" + \
                "\nVersões disponíveis:\n\n" + \
                "\n".join(nomes_das_versoes))

        versao = args[0]

        try:
            funcao = versoes_disponiveis[versao]
        except KeyError:
            raise CommandError("\nVersões disponíveis:\n\n" + \
                "\n".join(nomes_das_versoes))

        funcao(self, *args[1:])
