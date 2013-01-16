################################
Registro de mudanças - CHANGELOG
################################

v1.2.1
------

- Correção: relatório anual passa a funcionar -- havia um bug no
  *template* que exibia um erro na hora de gerar o relatório.

- Inversão do sinal dos 10% a pagar -- um mostrador *maior que zero*
  significa que *há dívida*. O outro jeito parecia causar muita
  confusão.

- Vários testes relativos aos 10% a pagar -- feitos pra assegurar que
  os cálculos estão sendo feitos corretamente.


v1.2.0
------

- Aparência: criação de uma barra no topo da aplicação para acesso às
  diferentes telas do sistema.

- Funcionalidade: edição direta das transações de contabilidade relativas aos
  10% a pagar -- futuramente será expandida para todas as transações do
  sistema.

- :ref:`Novo sistema de versionamento <desenvolvimento-versoes>`

- Funcionalidade: configuração da divisão dos 10% de cada venda entre os
  funcionários e a casa.

- Mudanças no relatório "Despesas Agrupadas por Categoria":
    - Conserto: agora as categorias são corretamente agrupadas
    - Linha de rodapé exibindo o total de despesas
    - Colunas exibindo, para cada categoria, o percentual de suas despesas
      com relação ao total de despesas e com relação ao total de vendas do
      período.

