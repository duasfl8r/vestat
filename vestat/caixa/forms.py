# -*- encoding: utf-8 -*-
import django.forms
from models import Dia, DespesaDeCaixa, MovimentacaoBancaria, CategoriaDeMovimentacao, AjusteDeCaixa, \
    Venda, PagamentoComCartao, Bandeira

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

    choices = sorted(
        [(c.id, c.nome_completo) for c in CategoriaDeMovimentacao.objects.all()],
        key=lambda t: t[1]
    )

    coerce = lambda id: CategoriaDeMovimentacao.objects.get(pk=id)

    categoria = django.forms.TypedChoiceField(label="Categoria", choices=choices,
        coerce=coerce, empty_value=None, required=False)

class MovimentacaoBancariaForm(LocalizedModelForm):
    class Meta:
        model = MovimentacaoBancaria

    choices = sorted(
        [(c.id, c.nome_completo) for c in CategoriaDeMovimentacao.objects.all()],
        key=lambda t: t[1]
    )

    coerce = lambda id: CategoriaDeMovimentacao.objects.get(pk=id)

    categoria = django.forms.TypedChoiceField(label="Categoria", choices=choices,
        coerce=coerce, empty_value=None, required=False)

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

    bandeira = django.forms.models.ModelChoiceField(queryset=Bandeira.objects.filter(ativa=True))

class BandeiraForm(LocalizedModelForm):
    class Meta:
        model = Bandeira
