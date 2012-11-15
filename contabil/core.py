# -*- encoding: utf-8 -*-
SEPARADOR_DE_CONTAS = ":"

def join(*contas):
    """
    Junta as contas dadas usando o símbolo separador em
    `SEPARADOR_DE_CONTAS`.

    """

    for conta in contas:
        assert isinstance(conta, basestring)

    return SEPARADOR_DE_CONTAS.join(contas)


class Contas:
    """
    Fornece métodos para construir e inquirir uma hierarquia de contas
    financeiras.

    """

    def __init__(self):
        self._hierarquia = {
            "lancamentos": [],
            "contas": {},
        }

    def __eq__(self, other):
        return self._hierarquia == other._hierarquia


    def digerir_registro(self, registro):
        """
        Alimenta o objeto com contas tiradas de um registro de
        transações.

        Argumentos:

        - registro: objeto `models.Registro`.

        """

        self.digerir_transacoes(registro.transacoes.all())

    def digerir_transacoes(self, transacoes):
        """
        Alimenta o objeto com contas tiradas de transações.

        Argumentos:

        - transacoes: um iterable contendo objetos `models.Transacao`.

        """

        for transacao in transacoes:
            self.digerir_lancamentos(transacao.lancamentos.all())

    def digerir_lancamentos(self, lancamentos):
        """
        Alimenta o objeto com contas tiradas de lançamentos.

        Argumentos:

        - lancamentos: um iterable contendo objetos `models.Lancamento`.

        """

        for lancamento in lancamentos:
            self.digerir_lancamento(lancamento)

    def digerir_lancamento(self, lancamento):
        """
        Alimenta o objeto com o lançamento dada.

        Argumentos:

        - lancamento: um objeto `models.Lancamento`

        """

        contas = lancamento.conta.split(SEPARADOR_DE_CONTAS)

        pai = self._hierarquia
        for conta in contas:
            if conta not in pai["contas"]:
                pai["contas"][conta] = {
                    "lancamentos": [],
                    "contas": {},
                }

            pai = pai["contas"][conta]

        pai["lancamentos"].append(lancamento)

    @property
    def dict(self):
        """
        Retorna um `dict` representando a hierarquia de contas com as
        quais o objeto foi alimentado.

        O dicionário retornado é uma estrutura recursiva, onde cada
        conta tem o seguinte formato:

        {
            "contas": {
                CONTA_1: {
                    "contas": {
                        ...
                    },

                    "lancamentos": [
                        ...
                    ]
                },

                CONTA_2: {
                    "contas": {
                        ...
                    },

                    "lancamentos": [
                        ...
                    ]
                },

                ...
            }

            "lancamentos": [
                LANCAMENTO_1,
                LANCAMENTO_2,
                LANCAMENTO_3,
                ...
            ]
        }

        onde cada chave do `dict` "contas" é o nome de uma subconta, e
        seu valor é um dicionário com a mesma estrutura do pai;

        e cada elemento da lista "lancamentos" é um objeto
        `models.Lancamento`, representando um lançamento categorizada
        nessa conta.

        Contas sem filhos possuem uma lista vazia no valor de "contas".

        """

        return self._hierarquia
