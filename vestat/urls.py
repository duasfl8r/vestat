# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin

import vestat.caixa.urls
import vestat.relatorios.urls
import vestat.config.urls
import vestat.calendario.urls

import views
from vestat.settings import MEDIA_ROOT


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^vestat/', include('vestat.foo.urls')),

     (r'^admin/', include(admin.site.urls)),
     (r'^$', views.index),
     (r'^caixa/', include(vestat.caixa.urls)),
     (r'^config/', include(vestat.config.urls)),
     (r'^relatorios/', include(vestat.relatorios.urls)),
     (r'^calendario/', include(vestat.calendario.urls, namespace="calendario")),
     (r'^m/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': MEDIA_ROOT}),
)

handler500 = 'views.server_error'
