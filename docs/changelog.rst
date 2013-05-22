################################
Registro de mudanças - CHANGELOG
################################

v1.2.2
------

Comando de atualização do BD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Algumas das mudanças feitas no programa alteram o modelo do banco de dados.

Pra atualizar pra versão 1.2.2, é necessário exportar o banco de dados antigo
para um arquivo JSON, e rodar um script pra modificar esse dump para atender ao
novo modelo e importá-lo num novo banco de dados.

Pra exportar, rode ``python manage.py dumpdata exportado.json``.

Em seguida, rode  ``python manage.py atualizar 1.2.2 exportado.json``.

Configurações do programa
^^^^^^^^^^^^^^^^^^^^^^^^^

- O aplicativo 'config' foi incrementado com um sistema pra que cada
  aplicativo possa adicionar seus próprios links na tela Configurações do
  programa.

Calendário
^^^^^^^^^^

- Adiciona a tela **Calendário** no programa. Essa tela mostra calendários de
  cada mês, permitindo que cada aplicativo do django cadastre seus próprios
  eventos.

Feriados
^^^^^^^^

- Cria o **aplicativo 'feriados'**, que permite cadastrar feriados fixos e
  móveis (dependentes da data da Páscoa), consultar se um determinado dia é
  feriado e listar os feriados entre duas datas. Sua função inicial é pra pular
  os feriados bancários na contagem de dias de depósito de um pagamento com
  cartão.

- **Tela de edição de feriados**: através da tela de Configurações, é possível
  adicionar, editar e remover feriados.

- **Cadastra os feriados como eventos do calendário**.

- **Remove o antigo sistema de feriados**, que envolvia marcar um *checkbox* na
  tela do caixa, e que não era usado.

- Parte do script descrito na seção *Comando de atualização do BD* **cadastra os
  feriados bancários do Brasil** no banco de dados.

Bandeiras e pagamentos com cartão
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Contagem de dias pro depósito**: Adiciona os atributos "prazo de depósito"
  (e.g. "30 dias", "2 dias") e "contagem de dias" ("dias úteis" ou "dias
  corridos") nas bandeiras. Através deles, é possível calcular quando o
  pagamento será depositado em conta corrente.

- **Evento de depósito de pagamento**: mostra, pra cada dia no calendário, o
  total a ser depositado pelas bandeiras referentes aos pagamentos feitos por
  clientes do restaurante, usando os novos atributos descritos acima.

- **Bandeiras ativas/inativas**: como os pagamentos com cartão ficam atrelados
  à bandeira no banco de dados, mudar os dados de uma bandeira mudaria todos os
  pagamentos que tenham usado essa bandeira no passado. Foi adicionado um atributo
  **ativa** nas bandeiras, e o modo certo de lidar com uma mudança de taxa ou
  de dias de depósito de uma bandeira é desativá-la e criar uma nova bandeira
  com os dados atualizados. Bandeiras inativas não aparecem pra serem
  selecionadas na tela de fechar uma venda.

- **Tela de edição de bandeiras**: através da tela de Configurações, é possível
  adicionar, editar, desativar e remover as bandeiras.

Categorias de movimentação
^^^^^^^^^^^^^^^^^^^^^^^^^^

- As categorias de *Despesas de Caixa* e *Movimentaçãoes Bancárias* foram
  migradas pra um novo sistema. Antes modificáveis somente pelo código-fonte e
  sem capacidade da aninhamento, agora as categorias podem ser modificadas pelo
  próprio programa, e podem ter categorias-filhas (e.g. "Fornecedores > Bebidas").

- **Migração de categorias**: parte do script descrito na seção *Comando de
  atualização do BD* cria categorias pro novo modelo e migra as despesas de
  caixa e movimentações bancárias do banco de dados pra usar as novas
  categorias, de acordo com uma tabela associativa feita pelo cliente.

- **Tela de edição de categorias, despesas de caixa e movimentações
  bancárias**: através da tela de Configurações, é possível adicionar, editar e
  remover categorias, despesas de caixa e movimentações bancárias.

Relatórios
^^^^^^^^^^

- **Novo sistema interno de relatórios**: o módulo ``reports2`` do aplicativo
  ``relatorios`` cria um novo sistema de relatórios, que permite ter outros
  tipos de componentes além de tabelas (como gráficos).

- **Relatório de meses**: o "relatório anual" foi substituído pelo "relatório
  de meses". Em vez de mostrar somente os meses de um determinado ano, ele
  mostra os **meses de um intervalo** ("janeiro de 2012 a março de 2013"). Além da
  mesma tabela presente no relatório anual, também são exibidos **três gráficos
  de barras**: *despesas por mês*, *faturamentos por mês*, *resultados por
  mês*. Os três gráficos exibem também linhas de tendência no intervalo
  fornecido.

Outras mudanças
^^^^^^^^^^^^^^^

- Código-fonte atualizado pro **Django 1.5**.

- A documentação define a licença GNU General Public License versão
  3 (GPLv3) pra todo o código-fonte do programa.

- Ao fechar uma venda, focaliza e seleciona o campo de "hora de saída",
  permitindo que se edite ele simplesmente digitando a hora certa.

- Exibe links pros dias de trabalho (tela "Caixa" do dia) no calendário.

- O arquivo de banco de dados do Vestat agora fica num diretório separado -- o
  "diretório de dados do usuário" determinado pelo módulo python ``appdirs``.

- Correção: todos os formatos de datas no relatório de despesas agora são no
  formato DD/MM/AAAA

- Sistema de armazenamento de arquivos temporários (módulo ``temp.py``):
  funções pra criar arquivos temporários e limpar arquivos antigos -- usada pra
  gerar gráficos.

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

