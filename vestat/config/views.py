from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext

from core import config_pages


def config_page(request, name):
    try:
        page = config_pages[name]
    except KeyError:
        raise Http404

    return render_to_response("config_page.html", {
            "page": page,
        },
        context_instance=RequestContext(request))
