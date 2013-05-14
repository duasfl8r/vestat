# -*- encoding: utf-8 -*-
from django.conf.urls.defaults import *

from views import EventsCalendarView

urlpatterns = patterns('',
     url(r'^(\d{4})/(\d{2})/$', EventsCalendarView.as_view(), name="events_calendar"),
)
