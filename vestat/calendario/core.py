# -*- encoding: utf-8 -*-
import logging
from django.conf import settings

logger = logging.getLogger("vestat")

class Event():
    def __init__(self, date, text, description=None):
        self.date = date
        self.text = text
        self.description = description if description else ""

def get_events(begin, end):
    event_list = []

    for app in settings.INSTALLED_APPS:
        events_module_name = app + ".events"

        try:
            module = __import__(events_module_name, fromlist=["events"])
        except ImportError:
            pass
        else:
            generators = [i for i in vars(module).items() if i[0].endswith("events")]

            for name, function in generators:
                result = list(function(begin, end))
                event_list.extend(result)

    return sorted(event_list, key=lambda e: e.date)
