# -*- encoding: utf-8 -*-

"""
Classes e funções utilitárias que dependem do Django.
"""

import django.forms

class LocalizedModelForm(django.forms.ModelForm):
    """
    Estende o `ModelForm` do django, tornando os campos `DecimalField`
    *localized* -- com a formatação dependente do *locale* do sistema.

    """

    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelForm, cls).__new__(cls, *args, **kwargs)
        for field in new_class.base_fields.values():
            if isinstance(field, django.forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True
        return new_class

