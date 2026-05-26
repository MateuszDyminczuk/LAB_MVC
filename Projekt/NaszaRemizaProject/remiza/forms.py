from django import forms
from .models import Strazak, Pojazd, Akcja, Sprzet


class StrazakForm(forms.ModelForm):
    
    username = forms.CharField(
        max_length=150, 
        required=True, 
        label="Nazwa użytkownika (Login)",
        widget=forms.TextInput(attrs={'placeholder': 'np. k.nowak'})
    )
    password = forms.CharField(
        required=True, 
        label="Hasło początkowe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Min. 8 znaków'})
    )

    class Meta:
        model = Strazak
        fields = ['username', 'password', 'imie', 'nazwisko', 'stopien', 'data_badan']

class PojazdForm(forms.ModelForm):
    class Meta:
        model = Pojazd
        fields = ['nazwa', 'oznaczenie', 'numer_operacyjny', 'sprawny', 'data_przegladu','data_oc' ]

class AkcjaForm(forms.ModelForm):
    class Meta:
        model = Akcja
        fields = [
            'numer_zdarzenia', 
            'rodzaj', 
            'miejsce', 
            'data_godzina_wyjazdu', 
            'data_godzina_powrotu', 
            'dowodca', 
            'pojazdy',  
            'ratownicy', 
            'opis'
        ]
        
        widgets = {
            'data_godzina_wyjazdu': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'data_godzina_powrotu': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'opis': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            
            
            'pojazdy': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-grid-item'}),
            'ratownicy': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-grid-item'}),
        }   



class SprzetForm(forms.ModelForm):
    class Meta:
        model = Sprzet
        fields = ['nazwa', 'producent', 'model', 'numer_inwentarzowy', 'data_zakupu', 'sprawny', 'notatki']
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Piła łańcuchowa'}),
            'producent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Stihl'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. MS 261'}),
            'numer_inwentarzowy': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. OSP/S/02'}),
            'data_zakupu': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sprawny': forms.CheckboxInput(attrs={'style': 'width: 20px; height: 20px; accent-color: #28a745;'}),
            'notatki': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Wpisz uwagi, np. Wymieniono świecę i filtr 12.2025'}),
        }
