.. _feriados:

########
Feriados
########

O aplicativo ``feriados`` permite o cadastramento de feriados no banco
de dados, consultar se um determinado dia é feriado e listar os feriados entre
duas datas.

Esse aplicativo se manifesta pro usuário como a marcação de feriados no
calendário, e podem ser editados através da tela de configurações.

Os feriados são usados para calcular o dia que um pagamento com cartão de
crédito cai em conta corrente: ver
``caixa.PagamentoComCartao.data_de_deposito``.

Tipos de feriado
================

Os feriados são divididos em três tipos, de acordo com sua data:

- **Feriados anuais fixos**: são feriados que acontecem todos os anos numa data
  fixa (mês e dia). Por exemplo, o Natal sempre acontece no dia 25 de dezembro.

- **Feriados anuais móveis**: são feriados que acontecem todos os anos, mas com
  data variável de acordo com a Páscoa. Por exemplo, o Corpus Christi acontece
  60 dias após a Páscoa.

- **Feriado de data única**: são feriados que acontecem uma única vez, em um
  único ano. Isso é uma solução pra cadastrar dias enforcados.

Adicionar/editar/remover feriados
=================================

1. Entre na tela de configurações, clicando em ``Configurações`` no menu do topo.

2. Clique no link ``Feriados`` -- você será levado a uma listagem de todos os feriados cadastrados no banco de dados.

3. Para **adicionar** um feriado, clique no botão ``Adicionar feriado +`` no
   canto superior direito -- você será levado à tela de adicionar feriado (veja abaixo).

   Para **remover** um feriado, marque a *checkbox* correspondente a ele na
   lista, selecione *Remover feriados selecionados* no campo ``Ação``, e clique
   em ``Ir``. Confirme a remoção.

   Para **editar** um feriado, clique em seu nome ou em sua data -- você será
   levado à tela de modificar feriado (veja abaixo).

4. Um feriado possui um campo de nome, e três campos de data. Você deve
   preencher o nome do feriado e *somente um* dos campos de data, de acordo com
   o tipo do feriado (veja "Tipos de feriado" acima).

   O campo **data única**, se preenchido, deve conter uma data no formato ``DD/MM/AAAA``.

   O campo **data anual fixa**, se preenchido, deve conter uma data no formato ``DD/MM``.

   O campo **Data móvel**, se preenchido, deve conter uma expressão aritmética,
   com 'pascoa' significando o dia da páscoa e com os dias envolvidos por
   ``d(...)``. Por exemplo, o Corpus Christi é definido por ``pascoa + d(60)``.

.. _feriados-calendario:

Feriados no calendário
======================

Os feriados são cadastrados como eventos do calendário, sendo exibidos na tela
"Calendário".

Links
=====

* `Legislação dos feriados bancários <http://www.sato.adm.br/guiadp/paginas/trib_feriado_bancario.htm>`_
* `Feriados no Brasil <http://pt.wikipedia.org/wiki/Feriados_no_Brasil>`_
