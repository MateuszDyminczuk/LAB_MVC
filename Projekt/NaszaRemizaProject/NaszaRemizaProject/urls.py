"""
URL configuration for NaszaRemizaProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from remiza.admin import admin_site
from django.urls import path
from remiza.views import login_view, statystyki_dashboard
from remiza.views import index_view
from remiza.views import logout_view;
from remiza.views import strazacy_lista;
from remiza.views import edytuj_strazaka;
from remiza.views import dodaj_strazaka;
from remiza.views import usun_strazaka;
from remiza.views import pojazdy_lista;
from remiza.views import edytuj_pojazd;
from remiza.views import usun_pojazd;
from remiza.views import dodaj_pojazd;
from remiza.views import dodaj_akcje;
from remiza.views import wyjazdy_view;
from remiza.views import szczegoly_akcji;
from remiza.views import edytuj_akcje;
from remiza.views import usun_akcje;
from remiza.views import sprzet_lista, dodaj_sprzet, edytuj_sprzet, usun_sprzet
from remiza.views import zapisz_wydarzenie, usun_wydarzenie;
from remiza.views import moj_profil;

urlpatterns = [
    path('admin/', admin_site.urls),
    path('login/', login_view, name='login'),
    path('', index_view, name='index'),
    path('logout/', logout_view, name='logout'),
    path('strazacy/', strazacy_lista, name='strazacy_view'),
    path('strazacy/edytuj/<int:pk>/', edytuj_strazaka, name='edytuj_strazaka'),
    path('strazacy/dodaj/', dodaj_strazaka, name='dodaj_strazaka'),
    path('strazacy/usun/<int:pk>/', usun_strazaka, name='usun_strazaka'),
    path('pojazdy/', pojazdy_lista, name='pojazdy_view'),
    path('pojazdy/edytuj/<int:pk>/', edytuj_pojazd, name='edytuj_pojazd'),
    path('pojazdy/usun/<int:pk>/', usun_pojazd, name='usun_pojazd'),
    path('pojazdy/dodaj/', dodaj_pojazd, name='dodaj_pojazd'),
    path('wyjazdy/dodaj/', dodaj_akcje, name='dodaj_akcje'),
    path('wyjazdy/', wyjazdy_view, name='wyjazdy_view'),
    path('wyjazdy/<int:akcja_id>/', szczegoly_akcji, name='szczegoly_akcji'),
    path('wyjazdy/<int:akcja_id>/edycja/', edytuj_akcje, name='edytuj_akcje'),
    path('wyjazdy/<int:akcja_id>/usun/', usun_akcje, name='usun_akcje'),
    path('sprzet/', sprzet_lista, name='sprzet_lista'),
    path('sprzet/dodaj/', dodaj_sprzet, name='dodaj_sprzet'),
    path('sprzet/<int:sprzet_id>/edycja/', edytuj_sprzet, name='edytuj_sprzet'),
    path('sprzet/<int:sprzet_id>/usun/', usun_sprzet, name='usun_sprzet'),
    path('wydarzenia/zapisz/', zapisz_wydarzenie, name='zapisz_wydarzenie'),
    path('wydarzenia/usun/', usun_wydarzenie, name='usun_wydarzenie'),
    path('profil/', moj_profil, name='moj_profil'),
    path('statystyki/', statystyki_dashboard, name='statystyki_dashboard'),
]
