#############################
Passo-a-passo de atualizações
#############################

1.2.1 pra 1.2.2
===============

#. Faça um backup do banco de dados (veja ref:`Banco de Dados <banco_de_dados>`).

#. Exportar os dados da versão antiga:
   #. Abrir a linha de comando no diretório de instalação do Vestat
   #. `python manage.py dumpdata caixa config contabil relatorios auth django_evolution > C:\dump_vestat_1.2.1.json`

#. Instalar novas dependências em `deps`

#. Se tudo deu certo, remover o arquivo de dump `C:\dump_vestat_1.2.1.json`
