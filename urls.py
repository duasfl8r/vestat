from django.conf.urls.defaults import *
from django.contrib import admin

import vestat.caixa.urls
import vestat.relatorios.urls
import vestat.config.urls
import views
from vestat.settings import BASE_DIR


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^vestat/', include('vestat.foo.urls')),

     (r'^admin/', include(admin.site.urls)),
     (r'^$', views.index),
     (r'^caixa/', include(vestat.caixa.urls)),
     (r'^relatorios/', include(vestat.relatorios.urls)),
     (r'^config/', include(vestat.config.urls)),
     (r'^m/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': BASE_DIR + '/media'}),
)
