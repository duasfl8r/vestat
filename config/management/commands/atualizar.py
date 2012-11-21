# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

def versao_1_2_0():
    # Sincroniza o banco de dados
    call_command('syncdb', interactive=False)

    # Evolui o banco de dados com o Django Evolution
    call_command('evolve', interactive=False, execute=True, hint=True, database="default")

    # Cria supe
    call_command('createsuperuser', interactive=False, username=settings.AUTOLOGIN_USERNAME, email="dev@lucasteixeira.com")

    # Configura a senha
    superuser = User.objects.get(username=settings.AUTOLOGIN_USERNAME)
    superuser.set_password(settings.AUTOLOGIN_PASSWORD)
    superuser.save()



class Command(BaseCommand):
    args = '<versao>'
    help = 'Faz as modificações necessárias para uma determinada versão'

    def handle(self, *args, **options):
        versoes_disponiveis = { nome.replace("versao_", "").replace("_", "."): item for nome, item in globals().items() if nome.startswith("versao_") }
        nomes_das_versoes = [ nome for nome, _ in versoes_disponiveis.items() ]

        if len(args) != 1:
            raise CommandError("Uso: atualizar " + self.args + "\n" + \
                "\nVersões disponíveis:\n\n" + \
                "\n".join(nomes_das_versoes))

        versao = args[0]

        try:
            funcao = versoes_disponiveis[versao]
        except KeyError:
            raise CommandError("\nVersões disponíveis:\n\n" + \
                "\n".join(nomes_das_versoes))

        funcao()
