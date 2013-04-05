# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('vestat.config.views',
     (r'^(?P<name>[a-zA-Z0-9_-]+)/$', 'config_page'),
)
