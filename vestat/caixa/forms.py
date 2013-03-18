import django.forms
from models import *

from vestat.django_utils import LocalizedModelForm

class DiaForm(LocalizedModelForm):
    class Meta:
        model = Dia

class AnotacoesForm(LocalizedModelForm):
    class Meta:
        model = Dia
        fields = ['anotacoes']
    anotacoes = django.forms.CharField(widget=django.forms.Textarea, required=False)

class DespesaDeCaixaForm(LocalizedModelForm):
    class Meta:
        model = DespesaDeCaixa

class MovimentacaoBancariaForm(LocalizedModelForm):
    class Meta:
        model = MovimentacaoBancaria

class AjusteDeCaixaForm(LocalizedModelForm):
    class Meta:
        model = AjusteDeCaixa

class VendaForm(LocalizedModelForm):
    class Meta:
        model = Venda

class AbrirVendaForm(LocalizedModelForm):
    class Meta:
        model = Venda
        fields = ['mesa', 'hora_entrada', 'num_pessoas', 'categoria', 'cidade_de_origem',
                  'pousada_que_indicou']

class FecharVendaForm(LocalizedModelForm):
    class Meta:
        model = Venda
        fields = ['hora_saida', 'conta', 'gorjeta', 'pgto_dinheiro', 'pgto_cheque']

class PagamentoComCartaoForm(LocalizedModelForm):
    class Meta:
        model = PagamentoComCartao
