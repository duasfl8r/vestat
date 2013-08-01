# -*- encoding: utf-8 -*-
from django import forms

class CalendarForm(forms.Form):
    """
    Formulário usado pra ver um mês do calendário.
    """
    year = forms.IntegerField(label=u"Ano", required=True)
    month = forms.IntegerField(label=u"Mês", max_value=12, min_value=1, required=True)
