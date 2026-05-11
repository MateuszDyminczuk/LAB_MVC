from django import forms
from .models import Strazak

class StrazakForm(forms.ModelForm):
    class Meta:
        model = Strazak
        fields = ['imie', 'nazwisko', 'stopien', 'data_badan']