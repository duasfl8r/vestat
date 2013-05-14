# -*- encoding: utf-8 -*-
from datetime import datetime
from django.conf import settings

def project_settings(request):
    """
    Adds the project settings to the context.

    """
    return {"project_settings": settings}

def data_hora(request):
    return {"agora": datetime.now()}
