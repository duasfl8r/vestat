from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
     (r'^$', index),
     (r'^resetar_bd/$', resetar_bd),
     (r'^exportar/$', exportar),
)
