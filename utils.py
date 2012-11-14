import django.forms

class LocalizedModelForm(django.forms.ModelForm):
    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelForm, cls).__new__(cls, *args, **kwargs)
        for field in new_class.base_fields.values():
            if isinstance(field, django.forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True
        return new_class
