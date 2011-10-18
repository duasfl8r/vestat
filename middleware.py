from django.conf import settings
from django.core.management import call_command
from django.contrib.messages.api import info

class AutocreateDatabaseMiddleware():
    def process_request(self, request):
        try:
            db_name = settings.DATABASES['default']['NAME']
            db = open(db_name)
            db.close()
        except IOError:
            call_command("syncdb", interactive=False)
            info(request, "Banco de dados criado.")