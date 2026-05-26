from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Strazak, Akcja, Pojazd, Sprzet, Wydarzenie
from .forms import StrazakForm, PojazdForm, AkcjaForm, SprzetForm
from django.utils import timezone
from datetime import date
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
    
    context = {
        'strazacy': wszyscy_strazacy,
        'ostatni_wyjazd': ostatni_wyjazd,
        'pojazdy': wszystkie_pojazdy,
        'wyjazdy': wszystkie_wyjazdy,         
        'wozy': wszystkie_pojazdy,   
        'druhowie': wszyscy_strazacy, 
        'wydarzenia': wszystkie_wydarzenia,
        'najblizsze_wydarzenia': najblizsze_wydarzenia, 
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

    if request.method == 'POST':
        form = StrazakForm(request.POST, instance=osoba)
        if form.is_valid():
            form.save()  
            return redirect('strazacy_view')
    else:
        form = StrazakForm(instance=osoba)

    return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'strazak': osoba})

@login_required
def dodaj_strazaka(request):
    if request.method == 'POST':
        form = StrazakForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Taki login jest już zajęty!")
                return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'tytul': 'Dodaj Strażaka'})
                
            nowy_user = User.objects.create_user(username=username, password=password)
            
            strazak = form.save(commit=False)
            strazak.user = nowy_user 
            strazak.save() 
            
            messages.success(request, f"Dodano strażaka {strazak.imie} {strazak.nazwisko} wraz z kontem.")
            return redirect('strazacy_view') 
    else:
        form = StrazakForm()
        
    return render(request, 'remiza/edytuj_strazaka.html', {'form': form, 'tytul': 'Dodaj Strażaka'})

@login_required
def usun_strazaka(request, pk):
    osoba = get_object_or_404(Strazak, pk=pk)
    osoba.delete()
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
            form.save()  
            return redirect('pojazdy_view')
    else:
        form = PojazdForm(instance=pojazd)

    return render(request, 'remiza/edytuj_pojazd.html', {'form': form, 'pojazd': pojazd})

@login_required 
def usun_pojazd(request, pk):
    pojazd = get_object_or_404(Pojazd, pk=pk)
    pojazd.delete()
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
            form.save()
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
        
    return render(request, 'remiza/dodaj_akcje.html', {'form': form})

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
    if request.method == 'POST':
        form = SprzetForm(request.POST)
        if form.is_valid():
            form.save()
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
            form.save()
            return redirect('sprzet_lista')
    else:
        form = SprzetForm(instance=sprzet)
    return render(request, 'remiza/sprzet_form.html', {'form': form, 'tytul': f'Edycja: {sprzet.nazwa}'})

@login_required
def usun_sprzet(request, sprzet_id):
    sprzet = get_object_or_404(Sprzet, id=sprzet_id)
    if request.method == 'POST':
        sprzet.delete()
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