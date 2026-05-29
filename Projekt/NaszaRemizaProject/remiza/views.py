from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Strazak, Akcja, Pojazd, Sprzet, Wydarzenie
from .forms import StrazakDodajForm, StrazakEdytujForm, PojazdForm, AkcjaForm, SprzetForm
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('index') 
            
    return render(request, 'remiza/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def index_view(request):
    wszyscy_strazacy = Strazak.objects.all().order_by('nazwisko')
    wszystkie_pojazdy = Pojazd.objects.all()
    
    try:
        ostatni_wyjazd = Akcja.objects.latest('data_godzina_wyjazdu')
    except Akcja.DoesNotExist:
        ostatni_wyjazd = None

    wszystkie_wyjazdy = Akcja.objects.all()
    wszystkie_wydarzenia = Wydarzenie.objects.all()
    najblizsze_wydarzenia = Wydarzenie.objects.filter(data__gte=date.today()).order_by('data')

    if request.user.is_superuser:
        strazacy_badania = wszyscy_strazacy
    else:
        strazacy_badania = Strazak.objects.filter(user=request.user)

    medycyna_lista = []
    for s in strazacy_badania:
        if s.data_badan:
            medycyna_lista.append({
                'tytul_wpisu': f"👨🏻‍⚕️ Badania: {s.imie} {s.nazwisko}",
                'data_badan': s.data_badan.strftime('%Y-%m-%d')
            })
        if s.waznosc_kpp:
            medycyna_lista.append({
                'tytul_wpisu': f"⛑️ Recertyfikacja KPP: {s.imie} {s.nazwisko}",
                'data_badan': s.waznosc_kpp.strftime('%Y-%m-%d')
            })

    # ====================================================================
    # NOWA LOGIKA: OBLICZANIE STATYSTYK DLA MINI-PANELU NA STRONIE GŁÓWNEJ
    # ====================================================================
    teraz = timezone.now()
    # Filtrujemy akcje tylko z bieżącego roku kalendarzowego
    akcje_rok = Akcja.objects.filter(
        data_godzina_wyjazdu__year=teraz.year, 
        data_godzina_powrotu__isnull=False
    )

    lacznie_wyjazdow = akcje_rok.count()
    lacznie_godzin = sum(akcja.zaokraglone_godziny() for akcja in akcje_rok)

    kategorie_konfiguracja = {
        'pozar': {'nazwa': 'Pożar', 'ikona': '🔥', 'klasa': 'pozar'},
        'wypadek': {'nazwa': 'Wypadek', 'ikona': '🚗', 'klasa': 'wypadek'},
        'miejscowe': {'nazwa': 'Miejscowe Zagrożenie', 'ikona': '🌪️', 'klasa': 'miejscowe'},
        'falszywy': {'nazwa': 'Alarm Fałszywy', 'ikona': '❌', 'klasa': 'falszywy'},
        'zabezpieczenie': {'nazwa': 'Zabezpieczenie Eventu', 'ikona': '🛡️', 'klasa': 'zabezpieczenie'},
        'gospodarczy': {'nazwa': 'Wyjazd Gospodarczy', 'ikona': '🛠️', 'klasa': 'gospodarczy'},
    }

    kategorie_stat = []
    for klucz, konfiguracja in kategorie_konfiguracja.items():
        liczba_wyjazdow_kat = akcje_rok.filter(rodzaj=klucz).count()
        kategorie_stat.append({
            'nazwa': konfiguracja['nazwa'],
            'ikona': konfiguracja['ikona'],
            'klasa': konfiguracja['klasa'],
            'wartosc': liczba_wyjazdow_kat
        })
    kategorie_stat = sorted(kategorie_stat, key=lambda x: x['wartosc'], reverse=True)

    wyjazdy_pojazdow = []
    for p in wszystkie_pojazdy:
        liczba_wyjazdów = akcje_rok.filter(pojazdy=p).count()
        if liczba_wyjazdów > 0: 
            wyjazdy_pojazdow.append({
                'nazwa': p.nazwa,
                'wyjazdy': liczba_wyjazdów
            })
    wyjazdy_pojazdow = sorted(wyjazdy_pojazdow, key=lambda x: x['wyjazdy'], reverse=True)
    # ====================================================================

    context = {
        'strazacy': wszyscy_strazacy,
        'ostatni_wyjazd': ostatni_wyjazd,
        'pojazdy': wszystkie_pojazdy,
        'wyjazdy': wszystkie_wyjazdy,         
        'wozy': wszystkie_pojazdy,   
        'druhowie': wszyscy_strazacy, 
        'wydarzenia': wszystkie_wydarzenia,
        'najblizsze_wydarzenia': najblizsze_wydarzenia,
        'strazacy_badania_json': medycyna_lista,
        
        # Przekazanie nowych zmiennych statystyk do szablonu base.html
        'lacznie_wyjazdow': lacznie_wyjazdow,
        'lacznie_godzin': lacznie_godzin,
        'kategorie_list': kategorie_stat,
        'wyjazdy_pojazdow': wyjazdy_pojazdow,
    }
    return render(request, 'remiza/base.html', context)

@login_required
def strazacy_lista(request):
    wyszukiwana_fraza = request.GET.get('szukaj')
    strazacy_z_bazy = Strazak.objects.all().order_by('nazwisko')

    if wyszukiwana_fraza:
        strazacy_z_bazy = strazacy_z_bazy.filter(nazwisko__icontains=wyszukiwana_fraza)

    context = {
        'lista_strazakow': strazacy_z_bazy,
    }
    return render(request, 'remiza/strazacy.html', context)

@login_required 
def edytuj_strazaka(request, pk):
    osoba = get_object_or_404(Strazak, pk=pk)
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do edycji danych strażaków!")
        return redirect('strazacy_view')

    if request.method == 'POST':
        form = StrazakEdytujForm(request.POST, instance=osoba)
        if form.is_valid():
            form.save()  
            messages.success(request, f"Zaktualizowano dane strażaka {osoba.imie} {osoba.nazwisko}.")
            return redirect('strazacy_view')
    else:
        form = StrazakEdytujForm(instance=osoba)

    return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'strazak': osoba})

@login_required
def dodaj_strazaka(request):
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do dodawania nowych strażaków!")
        return redirect('strazacy_view')

    if request.method == 'POST':
        form = StrazakDodajForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Taki login jest już zajęty!")
                return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'tytul': 'Dodaj Strażaka'})
                
            # Pobieramy stopień/funkcję z formularza
            stopien = form.cleaned_data.get('stopien')
            
            # Jeśli stopień to naczelnik, tworzymy superusera. W innym wypadku zwykłego użytkownika.
            if stopien == 'naczelnik':
                nowy_user = User.objects.create_superuser(username=username, password=password)
            else:
                nowy_user = User.objects.create_user(username=username, password=password)
            
            strazak = form.save(commit=False)
            strazak.user = nowy_user 
            strazak.save() 
            
            messages.success(request, f"Dodano strażaka {strazak.imie} {strazak.nazwisko} wraz z kontem administratora." if stopien == 'naczelnik' else f"Dodano strażaka {strazak.imie} {strazak.nazwisko} wraz z kontem.")
            return redirect('strazacy_view') 
    else:
        form = StrazakDodajForm()
        
    return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'tytul': 'Dodaj Strażaka'})

@login_required
def usun_strazaka(request, pk):
    osoba = get_object_or_404(Strazak, pk=pk)
    
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do usuwania strażaków z bazy!")
        return redirect('strazacy_view')

    osoba.delete()
    messages.success(request, "Strażak został pomyślnie usunięty.")
    return redirect('strazacy_view')

@login_required
def pojazdy_lista(request):
    wszystkie_pojazdy = Pojazd.objects.all().order_by('nazwa')
    context = {
        'lista_pojazdow': wszystkie_pojazdy,
    }
    return render(request, 'remiza/pojazdy.html', context)   

@login_required 
def edytuj_pojazd(request, pk):
    pojazd = get_object_or_404(Pojazd, pk=pk)

    if request.method == 'POST':
        form = PojazdForm(request.POST, instance=pojazd)
        if form.is_valid():
            if request.user.is_superuser:
                form.save()  
                messages.success(request, f"Zaktualizowano pełne dane pojazdu {pojazd.nazwa}.")
            else:
                oryginalny_pojazd = Pojazd.objects.get(pk=pk)
                oryginalny_pojazd.sprawny = form.cleaned_data['sprawny']
                oryginalny_pojazd.save()
                messages.success(request, f"Zmieniono status sprawności pojazdu {oryginalny_pojazd.nazwa}.")
                
            return redirect('pojazdy_view')
    else:
        form = PojazdForm(instance=pojazd)

    return render(request, 'remiza/edytuj_pojazd.html', {'form': form, 'pojazd': pojazd})

@login_required 
def usun_pojazd(request, pk):
    pojazd = get_object_or_404(Pojazd, pk=pk)
    
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do usuwania pojazdów bojowych!")
        return redirect('pojazdy_view')

    pojazd.delete()
    messages.success(request, "Pojazd został pomyślnie usunięty.")
    return redirect('pojazdy_view')

@login_required
def dodaj_pojazd(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Nie masz uprawnień do dodawania pojazdów.")
    if request.method == 'POST':
        form = PojazdForm(request.POST) 
        if form.is_valid():
            form.save() 
            return redirect('pojazdy_view')
    else:
        form = PojazdForm()

    return render(request, 'remiza/edytuj_pojazd.html', {'form': form, 'tytul': 'Dodaj Pojazd'})

@login_required
def wyjazdy_view(request):
    wszystkie_akcje = Akcja.objects.all().order_by('-data_godzina_wyjazdu')
    return render(request, 'remiza/wyjazdy.html', {'lista_akcji': wszystkie_akcje})

@login_required
def dodaj_akcje(request):
    if request.method == 'POST':
        form = AkcjaForm(request.POST)
        if form.is_valid():
            akcja = form.save(commit=False)
            
            slownik_pojazdow = {}
            slownik_sprzetu = {}
        
            pojazdy_w_akcji = form.cleaned_data.get('pojazdy', [])
            for p in pojazdy_w_akcji:
                klucz_post = f'licznik_pojazd_{p.id}'
                nowy_przebieg = request.POST.get(klucz_post)
                
                if nowy_przebieg:
                    nowy_przebieg_int = int(nowy_przebieg)
                    slownik_pojazdow[p.nazwa] = nowy_przebieg_int
                    
                    if nowy_przebieg_int > p.przebieg:
                        p.przebieg = nowy_przebieg_int
                        p.save()

            caly_sprzet = Sprzet.objects.filter(sprawny=True)
            for s in caly_sprzet:
                klucz_post = f'mth_sprzet_{s.id}'
                nowe_mth = request.POST.get(klucz_post)
                
                if nowe_mth:
                    nowe_mth_float = float(nowe_mth)
                    slownik_sprzetu[s.nazwa] = nowe_mth_float

                    if nowe_mth_float > s.motogodziny:
                        s.motogodziny = nowe_mth_float
                        s.save()

            akcja.liczniki_pojazdow_po = slownik_pojazdow
            akcja.motogodziny_sprzetu_po = slownik_sprzetu

            akcja.save()
            form.save_m2m()
            
            return redirect('wyjazdy_view')
    else:
        ostatnia_akcja = Akcja.objects.all().order_by('-id').first()
        
        if ostatnia_akcja:
            try:
                nowy_numer = int(ostatnia_akcja.numer_zdarzenia) + 1
            except ValueError:
                nowy_numer = ""
        else:
            nowy_numer = 1

        form = AkcjaForm(initial={'numer_zdarzenia': nowy_numer})
        
    return render(request, 'remiza/dodaj_akcje.html', {
        'form': form,
        'wszystkie_pojazdy': Pojazd.objects.all(),  
        'caly_sprzet': Sprzet.objects.filter(sprawny=True, czy_silnikowy=True)
    })

@login_required
def szczegoly_akcji(request, akcja_id):
    akcja = get_object_or_404(Akcja, id=akcja_id)
    return render(request, 'remiza/szczegoly_akcji.html', {'akcja': akcja})

@login_required
def edytuj_akcje(request, akcja_id):
    akcja = get_object_or_404(Akcja, id=akcja_id)
    
    if request.method == 'POST':
        form = AkcjaForm(request.POST, instance=akcja)
        if form.is_valid():
            form.save()
            return redirect('szczegoly_akcji', akcja_id=akcja.id)
    else:
        form = AkcjaForm(instance=akcja)
        
    return render(request, 'remiza/edytuj_akcje.html', {'form': form, 'akcja': akcja})

@login_required
def usun_akcje(request, akcja_id):
    akcja = get_object_or_404(Akcja, id=akcja_id)
    
    if request.method == 'POST':
        akcja.delete()
        return redirect('wyjazdy_view')
        
    return render(request, 'remiza/usun_akcje.html', {'akcja': akcja})

@login_required
def sprzet_lista(request):
    lista_sprzetu = Sprzet.objects.all().order_by('nazwa')
    return render(request, 'remiza/sprzet_lista.html', {'lista_sprzetu': lista_sprzetu})

@login_required
def dodaj_sprzet(request):
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do dodawania nowego sprzętu!")
        return redirect('sprzet_lista')

    if request.method == 'POST':
        form = SprzetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pomyślnie dodano nowy sprzęt do bazy.")
            return redirect('sprzet_lista')
    else:
        form = SprzetForm()
    return render(request, 'remiza/sprzet_form.html', {'form': form, 'tytul': 'Dodaj nowy sprzęt'})

@login_required
def edytuj_sprzet(request, sprzet_id):
    sprzet = get_object_or_404(Sprzet, id=sprzet_id)

    if request.method == 'POST':
        form = SprzetForm(request.POST, instance=sprzet)
        if form.is_valid():
            if request.user.is_superuser:
                form.save()
                messages.success(request, f"Zaktualizowano pełne dane sprzętu: {sprzet.nazwa}.")
            else:
                oryginalny_sprzet = Sprzet.objects.get(id=sprzet_id)
                oryginalny_sprzet.sprawny = form.cleaned_data['sprawny']
                oryginalny_sprzet.notatki = form.cleaned_data['notatki']
                oryginalny_sprzet.save()
                messages.success(request, f"Zaktualizowano stan sprawności/notatki dla: {oryginalny_sprzet.nazwa}.")
                
            return redirect('sprzet_lista')
    else:
        form = SprzetForm(instance=sprzet)
    return render(request, 'remiza/sprzet_form.html', {'form': form, 'tytul': f'Edycja: {sprzet.nazwa}', 'sprzet': sprzet})

@login_required
def usun_sprzet(request, sprzet_id):
    sprzet = get_object_or_404(Sprzet, id=sprzet_id)
    if not request.user.is_superuser:
        messages.error(request, "Nie masz uprawnień do usuwania sprzętu ze stanu jednostki!")
        return redirect('sprzet_lista')

    if request.method == 'POST':
        sprzet.delete()
        messages.success(request, "Sprzęt został pomyślnie usunięty z bazy.")
        return redirect('sprzet_lista')
        
    return render(request, 'remiza/usun_sprzet.html', {'sprzet': sprzet})

@login_required
def zapisz_wydarzenie(request):
    if request.method == 'POST':
        wydarzenie_id = request.POST.get('wydarzenie_id') 
        nazwa_wpisana = request.POST.get('nazwa')
        data_wpisana = request.POST.get('data')
        notatki_wpisane = request.POST.get('notatki', '')
        
        if nazwa_wpisana and data_wpisana:
            if wydarzenie_id:
                wydarzenie = get_object_or_404(Wydarzenie, id=wydarzenie_id)
                wydarzenie.nazwa = nazwa_wpisana
                wydarzenie.data = data_wpisana
                wydarzenie.notatki = notatki_wpisane
                wydarzenie.save() 
            else:
                wydarzenie = Wydarzenie.objects.create(
                    nazwa=nazwa_wpisana, 
                    data=data_wpisana, 
                    notatki=notatki_wpisane
                )
                
            return JsonResponse({
                'status': 'sukces', 
                'id': wydarzenie.id, 
                'nazwa': wydarzenie.nazwa,
                'notatki': wydarzenie.notatki
            })
            
    return JsonResponse({'status': 'blad'}, status=400)

@login_required
def usun_wydarzenie(request):
    if request.method == 'POST':
        wydarzenie_id = request.POST.get('wydarzenie_id')
        if wydarzenie_id:
            wydarzenie = get_object_or_404(Wydarzenie, id=wydarzenie_id)
            wydarzenie.delete()
            return JsonResponse({'status': 'sukces'})
            
    return JsonResponse({'status': 'blad'}, status=400)

@login_required
def moj_profil(request):
    try:
        strazak = request.user.profil_strazaka
    except AttributeError:
        strazak = None

    return render(request, 'remiza/moj_profil.html', {'strazak': strazak})

@login_required
def statystyki_dashboard(request):
    okres = request.GET.get('okres', 'rok')
    teraz = timezone.now()
    
    if okres == 'tydzień':
        data_od = teraz - timedelta(days=7)
    elif okres == 'miesiąc':
        data_od = teraz - timedelta(days=30)
    elif okres == 'kwartał':
        data_od = teraz - timedelta(days=90)
    else:  
        data_od = teraz - timedelta(days=365)
        okres = 'rok'

    akcje_okres = Akcja.objects.filter(data_godzina_wyjazdu__gte=data_od, data_godzina_powrotu__isnull=False)

    lacznie_wyjazdow = akcje_okres.count()
    lacznie_godzin = sum(akcja.zaokraglone_godziny() for akcja in akcje_okres)

    kategorie_konfiguracja = {
        'pozar': {'nazwa': 'Pożar', 'ikona': '🔥', 'klasa': 'pozar'},
        'wypadek': {'nazwa': 'Wypadek', 'ikona': '🚗', 'klasa': 'wypadek'},
        'miejscowe': {'nazwa': 'Miejscowe Zagrożenie', 'ikona': '🌪️', 'klasa': 'miejscowe'},
        'falszywy': {'nazwa': 'Alarm Fałszywy', 'ikona': '❌', 'klasa': 'falszywy'},
        'zabezpieczenie': {'nazwa': 'Zabezpieczenie Eventu', 'ikona': '🛡️', 'klasa': 'zabezpieczenie'},
        'gospodarczy': {'nazwa': 'Wyjazd Gospodarczy', 'ikona': '🛠️', 'klasa': 'gospodarczy'},
    }

    kategorie_stat = []
    for klucz, konfiguracja in kategorie_konfiguracja.items():
        liczba_wyjazdow_kat = akcje_okres.filter(rodzaj=klucz).count()
        
        kategorie_stat.append({
            'nazwa': konfiguracja['nazwa'],
            'ikona': konfiguracja['ikona'],
            'klasa': konfiguracja['klasa'],
            'wartosc': liczba_wyjazdow_kat
        })

    kategorie_stat = sorted(kategorie_stat, key=lambda x: x['wartosc'], reverse=True)

    wyjazdy_pojazdow = []
    wszystkie_pojazdy = Pojazd.objects.all()
    for p in wszystkie_pojazdy:
        liczba_wyjazdów = akcje_okres.filter(pojazdy=p).count()
        if liczba_wyjazdów > 0: 
            wyjazdy_pojazdow.append({
                'nazwa': p.nazwa,
                'wyjazdy': liczba_wyjazdów
            })

    wyjazdy_pojazdow = sorted(wyjazdy_pojazdow, key=lambda x: x['wyjazdy'], reverse=True)

    context = {
        'okres': okres,
        'lacznie_wyjazdow': lacznie_wyjazdow,
        'lacznie_godzin': lacznie_godzin,
        'kategorie_list': kategorie_stat, 
        'wyjazdy_pojazdow': wyjazdy_pojazdow,
    }

    return render(request, 'remiza/statystyki.html', context)