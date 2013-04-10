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


class FilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

    def filter(self, data):
        pass

    @property
    def filter_info(self):
        pass


class DateFilterForm(FilterForm):
    from_date = forms.DateField(label="Início", required=False)
    to_date = forms.DateField(label="Fim", required=False)

    def __init__(self, datefield_name="data", **kwargs):
        super(DateFilterForm, self).__init__(**kwargs)
        self.datefield_name = datefield_name

    def filter(self, data):
        filtered = data
        from_date, to_date = map(self.cleaned_data.get, ["from_date", "to_date"])

        if from_date:
            filtered = filtered.filter(**{ self.datefield_name + "__gte": from_date })
        if to_date:
            filtered = filtered.filter(**{ self.datefield_name + "__lte": to_date })

        return filtered


class AnoFilterForm(FilterForm):
    ano = forms.IntegerField(label="Ano", required=True)

    def __init__(self, datefield_name="data", **kwargs):
        super(AnoFilterForm, self).__init__(**kwargs)
        self.datefield_name = datefield_name

    def filter(self, data):
        ano = self.cleaned_data.get("ano")
        return data.filter(**{ self.datefield_name + "__year": ano })

    @property
    def filter_info(self):
        if self.is_bound:
            if self.is_valid():
                return "{0}".format(self.cleaned_data.get("ano"))
            else:
                return "Ano inválido"
        else:
            return ""

