# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('vestat.caixa.views',
     (r'^$', 'index'),

     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/$', 'ver_dia'),
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/criar$', 'criar_dia'),
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/remover$', 'remover_dia'),
     
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/imprimir$', 'imprimir_dia'),

     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/anotacoes$', 'anotacoes'),

     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/venda/adicionar$', 'adicionar_venda'),
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/venda/(?P<id>\d+)/entrada$', 'editar_venda_entrada'),
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/venda/(?P<id>\d+)/saida$', 'editar_venda_saida'),
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/venda/(?P<id>\d+)/abrir$', 'abrir_venda'),
     (r'^(\d{4})/(\d{2})/(\d{2})/venda/(?P<id>\d+)/remover$', 'remover_venda'),
     (r'^(\d{4})/(\d{2})/(\d{2})/venda/(?P<venda_id>\d+)/cartao/(?P<cartao_id>\d+)/remover$', 'remover_cartao'),

     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/despesa/adicionar$', 'adicionar_despesa'),
     (r'^(\d{4})/(\d{2})/(\d{2})/despesa/(?P<id>\d+)/remover$', 'remover_despesa'),
     
     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/ajuste/adicionar$', 'adicionar_ajuste'),
     (r'^(\d{4})/(\d{2})/(\d{2})/ajuste/(?P<id>\d+)/remover$', 'remover_ajuste'),

     (r'^(?P<ano>\d{4})/(?P<mes>\d{2})/(?P<dia>\d{2})/movbancaria/adicionar$', 'adicionar_movbancaria'),
     (r'^(\d{4})/(\d{2})/(\d{2})/movbancaria/(?P<id>\d+)/remover$', 'remover_movbancaria'),
)
