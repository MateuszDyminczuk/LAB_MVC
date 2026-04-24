from django.contrib import admin
from .models import Sprzet,Strazak,Pojazd, Akcja

@admin.register(Sprzet)
class SprzetAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'producent', 'model', 'data_zakupu', 'numer_inwentarzowy', 'sprawny',)
    list_filter = ('sprawny',)
    search_fields = ('nazwa', 'numer_inwentarzowy')

@admin.register(Strazak)
class StrazakAdmin(admin.ModelAdmin):
    list_display = ('nazwisko', 'imie', 'stopien', 'data_badan')
    list_filter = ('stopien',)
    search_fields = ('nazwisko',)

@admin.register(Pojazd)
class PojazdAdmin(admin.ModelAdmin):
    list_display = ('numer_operacyjny', 'nazwa', 'oznaczenie', 'sprawny')
    list_filter = ('sprawny',)

@admin.register(Akcja)
class AkcjaAdmin(admin.ModelAdmin):
    list_display = ('numer_zdarzenia', 'rodzaj', 'data_godzina_wyjazdu', 'miejsce', 'dowodca')
    list_filter = ('rodzaj',)
    search_fields = ('numer_zdarzenia', 'miejsce')
    filter_horizontal = ('ratownicy',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        pola_do_blokady = ['dowodca', 'pojazd']
        
        for pole in pola_do_blokady:
            if pole in form.base_fields:
                form.base_fields[pole].widget.can_add_related = False
                form.base_fields[pole].widget.can_change_related = False
                form.base_fields[pole].widget.can_delete_related = False
        
        return form