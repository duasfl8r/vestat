########################
Notas de Desenvolvimento
########################

.. _desenvolvimento-versoes:

Versões
=======

Cada *release* do Vestat possui um número de **versão**, no formato ``P.S.R``:

P - Primária
        Esse número é incrementado quando há uma mudança significativa no
        sistema, com novas funcionalidades grandes ou incompatíveis com a
        versão anterior.

S - Secundária
        Esse número é incrementado quando funcionalidades menores
        são acrescentadas.

R - Remendo
        Esse número é incrementado quando algum *bug* é consertado, mas não há
        nenhuma funcionalidade nova.

Por exemplo, ``1.2.3`` possui a versão *primária* ``1``, a versão *secundária*
``2``, e a versão "*remendo*" ``3``.

Release candidate
^^^^^^^^^^^^^^^^^

Na etapa de desenvolvimento em que o programa será testado pelo usuário, a
versão deve ser um **release candidate**.

O sufixo ``-rc1`` é acrescentado no final -- por exemplo, ``1.2.4-rc1``.

O programa é então usado em produção, e se não houver *bugs*, o sufixo desaparece.

Se forem relatados *bugs*, eles serão consertados e será testado um novo
*release candidate* -- no nosso exemplo, ``1.2.4-rc2``.

Repete-se o processo até o programa ficar estável e perder o sufixo.
