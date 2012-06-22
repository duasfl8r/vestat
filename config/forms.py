import django.forms
from models import *

class VestatConfigurationForm(django.forms.ModelForm):
    class Meta:
        model = VestatConfiguration
