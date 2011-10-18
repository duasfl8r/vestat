# -*- coding: utf-8 -*-
from django import forms

class RelatorioSimplesForm(forms.Form):
    de = forms.DateField(label="Início", required=False)
    ateh = forms.DateField(label="Fim", required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        de = cleaned_data.get("cc_myself")
        ateh = cleaned_data.get("subject")

        if de and ateh:
            if de > ateh:
                raise forms.ValidationError("A data de início deve ser antes da data de fim da filtragem.")

        return cleaned_data

class RelatorioAnualForm(forms.Form):
    ano = forms.IntegerField()
