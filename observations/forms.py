from django import forms
from datetime import date


class SelectDateForm(forms.Form):
    select_date = forms.DateField(required=False, initial=date.today())

    def __init__(self, *args, **kwargs):
        super(SelectDateForm, self).__init__(*args, **kwargs)
        self.fields['select_date'].widget.attrs.update({'class': 'datepicker'})
