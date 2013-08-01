#########
Glossário
#########

.. glossary::
        :sorted:

        tela
                Uma tela de interface com o usuário, através da qual o programa
                exibe informações e recebe *input*.

        aplicativo
                Um *aplicativo*, ou *aplicativo do django*, é um módulo python 

        10%
                Pagamento adicional ao total da :term:`venda`, feito por um :term:`cliente`.

                Idealmente equivale a 10% do valor total da venda, mas o valor
                real pago fica a critério do cliente.

                O valor acumulado dos 10% recebidos é dividido entre:

                #. A reposição de material no restaurante -- e.g. copos quebrados.
                #. O caixa do restaurante (**FIXME: é isso mesmo?**)
                #. Os funcionários do restaurante

        10% a pagar
                O total de parcelas dos 10% destinados aos funcionários é
                acumulado nos **10% a pagar**, um caixa imaginário.

                Quando ele atinge um certo valor, é feito o pagamento real aos
                funcionários.


        cliente
                Uma ou mais pessoas que dividem a mesma :term:`venda`.

                Um cliente senta-se numa certa mesa, paga um certo valor pela
                :term:`venda`, e os :term:`10%` relativos a esse valor.

        venda
                Uma transação comercial entre um :term:`cliente` e o
                restaurante.

                Não inclui os :term:`10%`.

        venda aberta
                Uma venda que ainda não foi concluída -- o :term:`cliente`
                ainda não fez o pagamento.

        venda fechada
                Uma venda que já foi concluída -- o :term:`cliente`
                já fez o pagamento.
