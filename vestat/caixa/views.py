# -*- encoding: utf-8 -*-
import datetime

from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib import messages

from models import *
from forms import *

def index(request):
    """Índice da webapp. Redireciona pro dia adequado."""

    agora = datetime.datetime.now()
    um_dia = datetime.timedelta(1)

    if agora.hour < 6: # é madrugada, contar como dia anterior
        agora -= um_dia

    return HttpResponseRedirect("/caixa/%04d/%02d/%02d" % (agora.year, agora.month, agora.day))

def criar_dia(request, ano, mes, dia):
    data = datetime.date(int(ano), int(mes), int(dia))

    try:
        dia = Dia.objects.get(data=data)
    except Dia.DoesNotExist:
        dia = Dia(data=data)
        dia.save()

    return redirect(dia)

def remover_dia(request, ano, mes, dia):
    data = datetime.date(int(ano), int(mes), int(dia))
    dia = get_object_or_404(Dia, data=data)
    dia.delete()
    return redirect(dia)

def anotacoes(request, ano, mes, dia):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    form_anotacoes = AnotacoesForm(instance=dia)

    if request.method == 'POST':
        form_anotacoes = AnotacoesForm(request.POST, instance=dia)
        if form_anotacoes.is_valid():
            form_anotacoes.save()
            return redirect(dia)

    return render_to_response('caixa/anotacoes.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_anotacoes': form_anotacoes,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))


def adicionar_venda(request, ano, mes, dia):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    form_venda = AbrirVendaForm()

    if request.method == 'POST':
        form_venda = AbrirVendaForm(request.POST)
        if form_venda.is_valid():
            venda = form_venda.save(commit=False)
            venda.dia = dia
            venda.save()
            return redirect(dia)

    return render_to_response('caixa/adicionar_venda.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_venda': form_venda,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def editar_venda_entrada(request, ano, mes, dia, id):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    venda = get_object_or_404(Venda, id=id)
    form_venda = AbrirVendaForm(instance=venda)

    if request.method == 'POST':
        form_venda = AbrirVendaForm(request.POST, instance=venda)
        if form_venda.is_valid():
            venda = form_venda.save()
            return redirect(dia)

    return render_to_response('caixa/adicionar_venda.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_venda': form_venda,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def editar_venda_saida(request, ano, mes, dia, id):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    venda = get_object_or_404(Venda, id=id)
    form_fechar_venda = FecharVendaForm(instance=venda)
    pgtos_cartao = venda.pagamentocomcartao_set.all()
    if pgtos_cartao is None: pgtos_cartao = []
    form_cartao = PagamentoComCartaoForm()
    erro = None

    if request.method == 'POST':
        if 'adicionar_pgto_cartao' in request.POST:
            form_fechar_venda = FecharVendaForm(request.POST, instance=venda)
            form_cartao = PagamentoComCartaoForm(request.POST)
            if form_cartao.is_valid():
                pgto_cartao = form_cartao.save(commit=False)
                pgto_cartao.venda = venda
                venda.pagamentocomcartao_set.add(pgto_cartao)
                venda.save()
            if form_fechar_venda.is_valid():
                venda = form_fechar_venda.save()
        elif 'fechar_venda' in request.POST:
            form_fechar_venda = FecharVendaForm(request.POST, instance=venda)
            if form_fechar_venda.is_valid():
                venda = form_fechar_venda.save()
                pgtos = [venda.pgto_dinheiro, venda.pgto_cheque, venda.pagamentocomcartao_set.aggregate(Sum('valor'))['valor__sum']]
                pgto_total = sum(filter(None, pgtos))
                if pgto_total == venda.conta:
                    venda.fechar()
                    venda.save()
                    return redirect(dia)
                else:
                    erro = mark_safe("Total da conta (<strong>%.2f</strong>) <strong>≠</strong> total de pagamentos (<strong>%.2f</strong>)" % (venda.conta, pgto_total))
        elif 'salvar_venda' in request.POST:
            form_fechar_venda = FecharVendaForm(request.POST, instance=venda)
            if form_fechar_venda.is_valid():
                venda = form_fechar_venda.save()
                venda.save()
                return redirect(venda.get_absolute_url() + "saida")

    return render_to_response('caixa/fechar_venda.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_fechar_venda': form_fechar_venda,
                              'pgtos_cartao': pgtos_cartao,
                              'form_cartao': form_cartao,
                              'erro': erro,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def editar_venda(request, ano, mes, dia, id):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    venda = get_object_or_404(Venda, id=id)
    form_venda = VendaForm(instance=venda)
    pgtos_cartao = venda.pagamentocomcartao_set.all()
    if pgtos_cartao is None: pgtos_cartao = []
    form_cartao = PagamentoComCartaoForm()
    erro = None

    if request.method == 'POST':
        if 'adicionar_pgto_cartao' in request.POST:
            form_venda = VendaForm(request.POST, instance=venda)
            form_cartao = PagamentoComCartaoForm(request.POST)
            if form_cartao.is_valid():
                pgto_cartao = form_cartao.save(commit=False)
                pgto_cartao.venda = venda
                venda.pagamentocomcartao_set.add(pgto_cartao)
                venda.save()
        else:
            form_venda = VendaForm(request.POST, instance=venda)
            if form_venda.is_valid():
                venda = form_venda.save()
                pgtos = [venda.pgto_dinheiro, venda.pgto_cheque, venda.pagamentocomcartao_set.aggregate(Sum('valor'))['valor__sum']]
                pgto_total = sum(filter(None, pgtos))
                if pgto_total == venda.conta:
                    venda.fechar()
                    venda.save()
                    return redirect(dia)
                else:
                    erro = mark_safe("Total da conta (<strong>%.2f</strong>) <strong>≠</strong> total de pagamentos (<strong>%.2f</strong>)" % (venda.conta, pgto_total))
    return render_to_response('caixa/editar_venda.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_venda': form_venda,
                              'erro': erro,
                              'pgtos_cartao': pgtos_cartao,
                              'form_cartao': form_cartao,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def abrir_venda(request, ano, mes, dia, id):
    venda = get_object_or_404(Venda, id=id)
    venda.abrir()
    venda.save()
    return redirect(venda.dia)

def adicionar_despesa(request, ano, mes, dia):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    form_despesa = DespesaDeCaixaForm()

    if request.method == 'POST':
        form_despesa = DespesaDeCaixaForm(request.POST)
        if form_despesa.is_valid():
            despesa = form_despesa.save(commit=False)
            despesa.dia = dia
            despesa.save()
            messages.success(request, "Despesa adicionada!")
            form_despesa = DespesaDeCaixaForm()

    return render_to_response('caixa/adicionar_despesa.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_despesa': form_despesa,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def adicionar_movbancaria(request, ano, mes, dia):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    form_movbancaria = MovimentacaoBancariaForm()

    if request.method == 'POST':
        form_movbancaria = MovimentacaoBancariaForm(request.POST)
        if form_movbancaria.is_valid():
            movbancaria = form_movbancaria.save(commit=False)
            movbancaria.dia = dia
            movbancaria.save()
            messages.success(request, "Movimentação bancária adicionada!")
            form_movbancaria = MovimentacaoBancariaForm()

    return render_to_response('caixa/adicionar_movbancaria.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_movbancaria': form_movbancaria,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def adicionar_ajuste(request, ano, mes, dia):
    data = datetime.date(*map(int, [ano, mes, dia]))
    dia = get_object_or_404(Dia, data=data)
    form_ajuste = AjusteDeCaixaForm()
    form_ajuste['valor'].css_classes('dinheiro')

    if request.method == 'POST':
        form_ajuste = AjusteDeCaixaForm(request.POST)
        if form_ajuste.is_valid():
            ajuste = form_ajuste.save(commit=False)
            ajuste.dia = dia
            ajuste.save()
            form_ajuste = AjusteDeCaixaForm()
            form_ajuste['valor'].css_classes('dinheiro')
            messages.success(request, "Ajuste adicionado!")

    return render_to_response('caixa/adicionar_ajuste.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                              'form_ajuste': form_ajuste,
                              'ajustes': dia.ajustedecaixa_set.all(),
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))


def imprimir_dia(request, ano, mes, dia):
    data = datetime.date(int(ano), int(mes), int(dia))
    dia = get_object_or_404(Dia, data=data)
    
    return render_to_response('caixa/imprimir_dia.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                             },
                             context_instance=RequestContext(request))

def ver_dia(request, ano, mes, dia, venda_id=None, despesa_id=None, movbancaria_id=None, fechar_venda=False):
    """Exibe e altera os dados de um determinado dia."""

    data = datetime.date(int(ano), int(mes), int(dia))

    try:
        dia = Dia.objects.get(data=data)
    except Dia.DoesNotExist:
        return render_to_response('caixa/criar_dia.html', {
                                    'title': "Dia: %s" % (data,),
                                    'data': data,
                                    'voltar_link': '/',
                                    'voltar_label': 'Módulos',
                                 },
                                 context_instance=RequestContext(request))

    #### NOVO FORMULARIO, EDITAR AQUI ####

    form_fechar_venda = FecharVendaForm()
    form_cartao = PagamentoComCartaoForm()
    pgtos_cartao = []
    esconder_fechar_venda_form = True

    form_venda = AbrirVendaForm()
    esconder_add_venda_form = True

    form_despesa = DespesaDeCaixaForm()
    esconder_add_despesa_form = True

    form_movbancaria = MovimentacaoBancariaForm()
    esconder_add_movbancaria_form = True


    #### NOVO FORMULARIO, EDITAR AQUI ####
    # EDITANDO / FECHANDO VENDA
    if venda_id:
        venda = get_object_or_404(Venda, id=venda_id)
        if request.method == 'POST':
            if 'adicionar_venda' in request.POST:
                # salvando venda editada
                form_venda = AbrirVendaForm(request.POST, instance=venda)
                if form_venda.is_valid():
                    venda = form_venda.save()
                    return HttpResponseRedirect(venda.dia.get_absolute_url())
                else:
                    esconder_add_venda_form = False
            elif 'fechar_venda' in request.POST:
                # fechando venda editada
                form_fechar_venda = FecharVendaForm(request.POST, instance=venda)
                if form_fechar_venda.is_valid():
                    venda = form_fechar_venda.save()
                    venda.fechar()
                    venda.save()
                    return HttpResponseRedirect(venda.dia.get_absolute_url())
                else:
                    esconder_fechar_venda_form = False
            elif "adicionar_pgto_cartao" in request.POST:
                form_fechar_venda = FecharVendaForm(request.POST)
                form_cartao = PagamentoComCartaoForm(request.POST)
                form_fechar_venda.is_valid()
                if form_cartao.is_valid():
                    pgto_cartao = form_cartao.save(commit=False)
                    pgto_cartao.venda = venda
                    venda.pagamentocomcartao_set.add(pgto_cartao)
                    venda.save()
                esconder_fechar_venda_form = False
        elif fechar_venda:
            # editando venda pra fechar
            form_fechar_venda = FecharVendaForm(instance=venda)
            pgtos_cartao = venda.pagamentocomcartao_set.all()
            esconder_fechar_venda_form = False
        else:
            # editando venda aberta
            form_venda = AbrirVendaForm(instance=venda)
            esconder_add_venda_form = False
    # EDITANDO DESPESA
    elif despesa_id:
        despesa = get_object_or_404(despesa, id=despesa_id)
        if request.method == 'POST':
            # enviando despesa editada
            form_despesa = DespesaDeCaixaForm(request.POST, instance=despesa)
            if form_despesa.is_valid():
                despesa = form_despesa.save()
                return HttpResponseRedirect(despesa.dia.get_absolute_url())
            else:
                esconder_add_despesa_form = False
        else:
            # pedido de edição
            form_despesa = despesaMiniForm(instance=despesa)
            esconder_add_despesa_form = False
    # EDITANDO MOVBANCARIA
    elif movbancaria_id:
        movbancaria = get_object_or_404(movbancaria, id=movbancaria_id)
        if request.method == 'POST':
            # enviando movbancaria editada
            form_movbancaria = MovimentacaoBancariaForm(request.POST, instance=movbancaria)
            if form_movbancaria.is_valid():
                movbancaria = form_movbancaria.save()
                return HttpResponseRedirect(movbancaria.dia.get_absolute_url())
            else:
                esconder_add_movbancaria_form = False
        else:
            # pedido de edição
            form_movbancaria = MovimentacaoBancariaForm(instance=movbancaria)
            esconder_add_movbancaria_form = False
    else:
        if request.method == 'POST':
            #### NOVO FORMULARIO, EDITAR AQUI ####
            if 'adicionar_venda' in request.POST:
                form_venda = AbrirVendaForm(request.POST)
                if form_venda.is_valid():
                    venda = form_venda.save(commit=False)
                    venda.dia = dia
                    venda.save()
                    form_venda = AbrirVendaForm()
                else:
                    esconder_add_venda_form = False
            if 'adicionar_despesa' in request.POST:
                form_despesa = DespesaDeCaixaForm(request.POST)
                if form_despesa.is_valid():
                    despesa = form_despesa.save(commit=False)
                    despesa.dia = dia
                    despesa.save()
                    form_despesa = DespesaDeCaixaForm()
                else:
                    esconder_add_despesa_form = False
            if 'adicionar_movbancaria' in request.POST:
                form_movbancaria = MovimentacaoBancariaForm(request.POST)
                if form_movbancaria.is_valid():
                    movbancaria = form_movbancaria.save(commit=False)
                    movbancaria.dia = dia
                    movbancaria.save()
                    form_movbancaria = MovimentacaoBancariaForm()
                else:
                    esconder_add_movbancaria_form = False

    return render_to_response('caixa/ver_dia.html', {
                              'title': "Dia: %s" % (dia.data,),
                              'dia': dia,
                              'data': data,
                               #### NOVO FORMULARIO, EDITAR AQUI ####
                              'form_venda': form_venda,
                              'form_cartao': form_cartao,
                              'pgtos_cartao': pgtos_cartao,
                              'esconder_add_venda_form': esconder_add_venda_form,
                              'form_fechar_venda': form_fechar_venda,
                              'esconder_fechar_venda_form': esconder_fechar_venda_form,
                              'form_despesa': form_despesa,
                              'esconder_add_despesa_form': esconder_add_despesa_form,
                              'form_movbancaria': form_movbancaria,
                              'esconder_add_movbancaria_form': esconder_add_movbancaria_form,
                              'movbancarias': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=True),
                              'taxas_cartao': dia.movimentacaobancaria_set.filter(pgto_cartao__isnull=False).\
                                  aggregate(Sum('valor'))['valor__sum'],
                              'voltar_link': '/',
                              'voltar_label': 'Módulos',
                             },
                             context_instance=RequestContext(request))

def remover_venda(request, id):
    venda = get_object_or_404(Venda, id=id)
    venda.delete()
    return redirect(venda.dia)

def remover_movbancaria(request, id):
    movbancaria = get_object_or_404(MovimentacaoBancaria, id=id)
    movbancaria.delete()
    return redirect(movbancaria.dia)

def remover_ajuste(request, id):
    ajuste = get_object_or_404(AjusteDeCaixa, id=id)
    ajuste.delete()
    return redirect(ajuste.dia)

def remover_despesa(request, id):
    despesa = get_object_or_404(DespesaDeCaixa, id=id)
    despesa.delete()
    return redirect(despesa.dia)

def remover_cartao(request, venda_id, cartao_id):
    venda = get_object_or_404(Venda, id=venda_id)
    cartao = get_object_or_404(PagamentoComCartao, id=cartao_id)
    cartao.delete()
    return redirect(venda.get_absolute_url() + "saida")
