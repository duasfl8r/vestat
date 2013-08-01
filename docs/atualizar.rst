###########
Atualizando
###########

1.2.1 pra 1.2.2
===============

#. Instalar as seguintes dependências (diretório ``deps``):
  * ``matplotlib-<versao>.exe``
  * ``numpy-<versao>.exe``
  * ``instalar_bundle.bat``

#. Faça um backup do banco de dados (veja ref:`Banco de Dados <banco_de_dados>`).

#. Exportar os dados da versão antiga:::

       cd C:\vestat\vestat\
       python manage.py dumpdata caixa config contabil relatorios django_evolution > C:\dump_vestat.json

#. Importar o dump, realizando as modificações pra torná-lo compatível com a versão 1.2.2:::

       cd C:\vestat\vestat\
       python manage.py atualizar 1.2.2 C:\dump_vestat.json

#. Remover o arquivo de dump ``C:\dump_vestat.json``
