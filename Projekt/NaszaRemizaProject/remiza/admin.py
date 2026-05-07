from django.contrib import admin
from .models import Sprzet, Strazak, Pojazd, Akcja
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User, Group

# 1. Funkcja statystyk zostaje bez zmian
def pobierz_statystyki():
    teraz = timezone.now()
    akcje_miesiac = Akcja.objects.filter(
        data_godzina_wyjazdu__month=teraz.month, 
        data_godzina_wyjazdu__year=teraz.year
    ).count()

    najczestszy_pojazd = Pojazd.objects.annotate(
        liczba_akcji=Count('akcja')
    ).order_by('-liczba_akcji').first()

    statystyki_rodzajow = Akcja.objects.values('rodzaj').annotate(
        ilosc=Count('rodzaj')
    ).order_by('-ilosc')

    return {
        'akcje_miesiac': akcje_miesiac,
        'najczestszy_pojazd': najczestszy_pojazd,
        'statystyki_rodzajow': statystyki_rodzajow,
    }

# 2. Definicje klas Admin (usuwamy dekoratory @admin.register)
class SprzetAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'producent', 'model', 'data_zakupu', 'numer_inwentarzowy', 'sprawny',)
    list_filter = ('sprawny',)
    search_fields = ('nazwa', 'numer_inwentarzowy')

class StrazakAdmin(admin.ModelAdmin):
    list_display = ('nazwisko', 'imie', 'stopien', 'data_badan', 'suma_godzin')
    list_filter = ('stopien',)
    search_fields = ('nazwisko',)

class PojazdAdmin(admin.ModelAdmin):
    list_display = ('numer_operacyjny', 'nazwa', 'oznaczenie', 'sprawny', 'liczba_wyjazdow_rok')
    list_filter = ('sprawny',)

class AkcjaAdmin(admin.ModelAdmin):
    list_display = ('numer_zdarzenia', 'rodzaj', 'data_godzina_wyjazdu', 'miejsce', 'dowodca', 'czas_trwania')
    list_filter = ('rodzaj',)
    search_fields = ('numer_zdarzenia', 'miejsce')
    filter_horizontal = ('ratownicy',)

# 3. Twoja niestandardowa strona admina
class NaszaRemizaAdminSite(admin.AdminSite):
    site_header = "System Zarządzania OSP - Panel Naczelnika"
    
    def index(self, request, extra_context=None):
        stats = pobierz_statystyki()
        extra_context = extra_context or {}
        extra_context.update(stats)
        return super().index(request, extra_context)

# 4. TWORZYMY OBIEKT I REJESTRUJEMY MODELE
admin_site = NaszaRemizaAdminSite(name='nasz_admin')

admin_site.register(Sprzet, SprzetAdmin)
admin_site.register(Strazak, StrazakAdmin)
admin_site.register(Pojazd, PojazdAdmin)
admin_site.register(Akcja, AkcjaAdmin)
admin_site.register(User) 
admin_site.register(Group) 