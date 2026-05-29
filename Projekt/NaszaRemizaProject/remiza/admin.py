from django.contrib import admin
from .models import Sprzet, Strazak, Pojazd, Akcja, Wydarzenie
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User, Group


def pobierz_statystyki():
    teraz = timezone.now()
    akcje_miesiac = Akcja.objects.filter(
        data_godzina_wyjazdu__month=teraz.month, 
        data_godzina_wyjazdu__year=teraz.year
    ).count()

    najczestszy_pojazd = Pojazd.objects.annotate(
        liczba_akcji=Count('akcje')
    ).order_by('-liczba_akcji').first()

    statystyki_rodzajow = Akcja.objects.values('rodzaj').annotate(
        ilosc=Count('rodzaj')
    ).order_by('-ilosc')

    return {
        'akcje_miesiac': akcje_miesiac,
        'najczestszy_pojazd': najczestszy_pojazd,
        'statystyki_rodzajow': statystyki_rodzajow,
    }


class SprzetAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'producent', 'model', 'data_zakupu', 'numer_inwentarzowy', 'sprawny',)
    list_filter = ('sprawny',)
    search_fields = ('nazwa', 'numer_inwentarzowy')

class StrazakAdmin(admin.ModelAdmin):
    list_display = ('nazwisko', 'imie', 'stopien', 'data_badan', 'suma_godzin')
    list_filter = ('stopien',)
    search_fields = ('nazwisko',)

@admin.register(Pojazd)
class PojazdAdmin(admin.ModelAdmin):
    list_display = ['nazwa', 'numer_operacyjny', 'data_przegladu', 'data_oc']

class AkcjaAdmin(admin.ModelAdmin):
    list_display = ('numer_zdarzenia', 'rodzaj', 'data_godzina_wyjazdu', 'miejsce', 'dowodca', 'czas_trwania')
    list_filter = ('rodzaj',)
    search_fields = ('numer_zdarzenia', 'miejsce')
    filter_horizontal = ('ratownicy',)


class NaszaRemizaAdminSite(admin.AdminSite):
    site_header = "System Zarządzania OSP - Panel Naczelnika"
    
    def index(self, request, extra_context=None):
        stats = pobierz_statystyki()
        extra_context = extra_context or {}
        extra_context.update(stats)
        return super().index(request, extra_context)


admin_site = NaszaRemizaAdminSite(name='nasz_admin')

admin_site.register(Sprzet, SprzetAdmin)
admin_site.register(Strazak, StrazakAdmin)
admin_site.register(Pojazd, PojazdAdmin)
admin_site.register(Akcja, AkcjaAdmin)
admin_site.register(User) 
admin_site.register(Group) 