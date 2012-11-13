from django.conf import settings

def project_settings(request):
    """
    Adds the project settings to the context.

    """
    return {"project_settings": settings}
