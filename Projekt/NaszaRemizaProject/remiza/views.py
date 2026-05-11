from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Strazak, Akcja, Pojazd
from .forms import StrazakForm



def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('index') 
            
    return render(request, 'remiza/login.html')


@login_required(login_url='login')
def index_view(request):
    return render(request, 'remiza/base.html') 


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def index_view(request):
    
    wszyscy_strazacy = Strazak.objects.all().order_by('nazwisko')
    try:
        ostatni_wyjazd = Akcja.objects.latest('data_godzina_wyjazdu')
    except Akcja.DoesNotExist:
        ostatni_wyjazd = None

    wszystkie_pojazdy = Pojazd.objects.all()
    
    context = {
        'strazacy': wszyscy_strazacy,
        'ostatni_wyjazd': ostatni_wyjazd,
        'pojazdy': wszystkie_pojazdy,
    }
    return render(request, 'remiza/base.html', context)

def strazacy_lista(request):
    wyszukiwana_fraza = request.GET.get('szukaj')
    strazacy_z_bazy = Strazak.objects.all().order_by('nazwisko')

    if wyszukiwana_fraza:
        strazacy = strazacy_z_bazy.filter(nazwisko__icontains=wyszukiwana_fraza)

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

