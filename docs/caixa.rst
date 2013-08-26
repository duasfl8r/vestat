##########
Tela Caixa
##########


Categorias de Movimentação
==========================

As *Despesas de Caixa* e *Movimentações Bancárias* possuem *categorias*.

Hierarquia de categorias
^^^^^^^^^^^^^^^^^^^^^^^^

As categorias podem ser organizadas em hierarquias -- cada uma pode possuir
subcategorias-filhas.

Ao editar as categorias (veja abaixo), preencher o campo **Mãe** de uma
categoria faz com que ela se torne uma subcategoria daquela definida no campo.

Assim, se editamos a categoria *Bebidas* e selecionamos a categoria
*Fornecedor* como sendo sua *mãe* (adicionada previamente), criamos a hierarquia
*Fornecedor > Bebidas*.

Adicionar/editar/remover categorias de movimentação
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Entre na tela de configurações, clicando em ``Configurações`` no menu do topo.

2. Clique no link ``Categorias de despesas de caixa e movimentações bancárias``
   -- você será levado a uma listagem de todos as categorias de movimentação
   cadastradas no banco de dados.

3. Para **adicionar** uma categoria, clique no botão ``Adicionar categoria de
   movimentação +`` no canto superior direito -- você será levado à tela de
   adicionar categoria (veja abaixo). Preencha os campos e salve.

   Para **remover** uma categoria, marque a *checkbox* correspondente a ela na
   lista, selecione *Remover categorias de movimentação selecionadas* no campo
   ``Ação``, e clique em ``Ir``. Confirme a remoção.

   Para **editar** uma categoria, clique em seu nome -- você será
   levado à tela de modificar categoria. Faça suas modificações e salve.



.. _caixa-pagamentos-com-cartao:

Pagamentos com Cartão
=====================

As vendas podem ser pagas com cartões de crédito ou débito.

Cada bandeira, assim como a opção de crédito ou débito, possui taxas e dias
para depósito em conta diferentes.

Prazo de depósito em conta
^^^^^^^^^^^^^^^^^^^^^^^^^^

Quando um cliente faz um pagamento com cartão, ele demora um certo tempo pra
ser depositado na conta corrente do restaurante pela bandeira.

Esse tempo é definido pelos campos **Dias até o depósito** e **Contagem de dias**
das bandeiras no banco de dados. O segundo campo determina se a contagem do
tempo é em dias corridos ou em dias úteis.

A contagem de tempo em dias úteis pula finais-de-semana e feriados cadastrados
(para ler mais sobre os feriados, consulte :ref:`Feriados <feriados>`).

Taxa retida pela bandeira
^^^^^^^^^^^^^^^^^^^^^^^^^

Cada bandeira retira uma certa porcentagem dos pagamentos. Essa porcentagem é
definida no campo **Taxa** das bandeiras no banco de dados.

Bandeiras ativas e inativas
^^^^^^^^^^^^^^^^^^^^^^^^^^^

O campo **Ativa?** de uma bandeira, quando marcado, permite que ela seja
escolhida ao fechar uma venda.

Como os pagamentos com cartão ficam atrelados à bandeira no banco de dados,
mudar os dados de uma bandeira mudaria todos os pagamentos que tenham usado
essa bandeira no passado.

Quando uma bandeira muda suas taxas, deve-se **desativar** a bandeira e criar
uma nova, possivelmente com o mesmo nome, com os novos dados.

Assim, os pagamentos antigos ainda usam a mesma taxa em seus cálculos, e os
pagamentos feitos de agora em diante usam a nova taxa.

Eventos no calendário
^^^^^^^^^^^^^^^^^^^^^

A :ref:`tela Calendário <calendario>` exibe os depósitos de pagamentos
efetuados pela bandeira em um determinado dia.

É exibido o valor total -- a soma dos pagamentos feitos por todas as bandeiras.
Ao colocar o mouse por cima desse valor, é exibida a listagem de todos os
pagamentos cujo depósito cai nesse dia, junto de seus valores brutos e da taxa
retirada de cada um deles.


Adicionar/editar/remover bandeiras
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Entre na tela de configurações, clicando em ``Configurações`` no menu do topo.

2. Clique no link ``Bandeiras de cartão de crédito/débito`` -- você será levado
   a uma listagem de todos as bandeiras cadastradas no banco de dados.

3. Para **adicionar** uma bandeira, clique no botão ``Adicionar bandeira +`` no
   canto superior direito -- você será levado à tela de adicionar bandeira
   (veja abaixo). Preencha os campos e salve.

   Para **remover** uma bandeira, marque a *checkbox* correspondente a ela na
   lista, selecione *Remover bandeiras selecionadas* no campo ``Ação``, e clique
   em ``Ir``. Confirme a remoção.

   Para **editar** uma bandeira, clique em seu nome -- você será
   levado à tela de modificar bandeira. Faça suas modificações e salve.

.. _caixa-10%:

10%
===

Para cada venda, também é recebido um valor chamado de **10%**.

Idealmente um décimo do valor da venda, na realidade o valor pago é
decidido pelo cliente. Por isso, o valor dos 10% é inserido manualmente,
e não calculado em cima do valor da venda.

Esses 10% pagos são divididos da seguinte maneira:

* Um décimo serve pra consertar copos e pratos quebrados, e outros pequenos
  gastos semelhantes.

* Uma certa parcela, chamada de **parcela da casa**, fica para o
  restaurante.

* Uma certa parcela, chamada de **parcela dos funcionários**, é dividida
  igualmente entre os funcionários do restaurante.

No programa, a parcela dos funcionários é acumulada em um mostrador
chamado **10% a pagar**, até atingir um valor significativo o suficiente
para ser pago aos funcionários.

Cálculo dos 10% a pagar
^^^^^^^^^^^^^^^^^^^^^^^

O valor dos *10% a pagar* é calculado da seguinte forma:

.. math::
    DaP =  \sum Divida_{10\% func} - \sum Despesa_{10\% func}

Onde:

* :math:`\sum Divida_{10\% func}` é a soma de todas as dívidas de 10% a
  pagar acumuladas com as vendas.

* :math:`\sum Despesa_{10\% func}` é a soma de todas as despesas de 10%
  pagos aos funcionários

Ou seja:

* um valor positivo (mostrado em **vermelho**) significa que se está devendo
  pros funcionários

* 0 significa que não há dívida

* um valor negativo (mostrado em **verde**) significa que se tem crédito com os
  funcionários para próximas dívidas de 10% a pagar.

Dívidas de 10% a pagar
----------------------

A cada venda fechada, é criada uma dívida de 10% a pagar pros funcionários
:math:`Divida_{10\% func}`, que é definida como:

.. math::
    Divida_{10\% func} = (Didiva_total * 0.9) * Frac_{func}

Onde:

* :math:`Divida_{total}` é o total dos 10% pagos pelo cliente
* :math:`Frac_{func}` é a fração dos funcionários

A fração dos funcionários :math:`Frac_{func}`, aplicada após retirar o décimo
destinado a pequenos consertos restaurante, é calculada da seguinte
forma:

.. math::
    Frac_{func} = Parcela_{func} / (Parcela_{func} + Parcela_{casa})

Onde:

* :math:`Parcela_{casa}`: é o valor de *Parcelas pra casa*
* :math:`Parcela_{func}`: é o valor de *Parcelas pros funcionários*


Despesas de 10% pagos aos funcionários
--------------------------------------

As despesas de caixa e bancárias da categoria *Pessoal - 10%*
representam pagamentos feitos aos funcionários para quitar a dívida de
10% a pagar.

Ajustando os 10% a pagar
^^^^^^^^^^^^^^^^^^^^^^^^

Para ajustar o valor dos 10% a pagar, basta criar uma transação na tela **Contabilidade**:

1. Na tela **Caixa**, anote o valor dos 10% a pagar do dia de hoje.

2. Calcule quanto deve ser somado aos 10% a pagar pra que ele
   atinja o valor desejado

   - Pra **zerar**, o valor deve ser o **oposto** do que está no
     mostrador.

    Por exemplo, se o mostrador exibe ``-420,25``, deve-se adicionar
    ``420,25`` para zerá-lo.

  - Para ajustar os *10% a pagar* para um valor ``X``, adicione o
    ``O + X``, onde ``O`` é o **oposto** do que está no mostrador..

    Por exemplo, se o mostrador exibe ``-420,25`` e queremos que ele
    fique em ``-30,00`` (devendo R$ 30)  deve-se adicionar ``420,25 +
    (-30) = 390,25``.

3. Abra a tela **Contabilidade**, na barra superior da tela.

4. Clique em **Adicionar transação**, no canto superior direito.

5. Preencha os campos:
   - **Data**: a data do ajuste -- provavelmente a data de hoje.
   - **Descrição**: "ajuste dos 10% a pagar", e talvez uma explicação
     do motivo do ajuste.

6. Na seção **Lançamentos**, preencha duas linhas, considerando ``A``
   como sendo o valor do ajuste:

   1. Valor: ``A``; Conta: ``dividas:contas a pagar:10%``
   2. Valor: ``-A``; Conta: ``ajustes:10% a pagar``

7. Clique em **Salvar**.


Isso efetivamente *soma o valor* à conta da dívida dos 10% a pagar
aos funcionários. Como a dívida tem um valor negativo, somar um valor
positivo à conta de fato *diminui a dívida*.

Como o sistema de contabilidade usado é de *dupla-entrada*, o
dinheiro somado à conta da dívida deve vir de algum lugar; é usada
uma "conta de ajustes" pra esse efeito.
