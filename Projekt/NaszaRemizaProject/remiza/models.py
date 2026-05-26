from django.db import models
from datetime import date

class Sprzet(models.Model):
    
    nazwa = models.CharField(max_length=100) 
    producent = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    numer_inwentarzowy = models.CharField(max_length=30, unique=True)
    data_zakupu = models.DateField()
    sprawny = models.BooleanField(default=True) 
    notatki = models.TextField(blank=True, verbose_name="Notatki / Serwis")

    class Meta:
        verbose_name = "Sprzęt"
        verbose_name_plural = "Sprzęt"

    def __str__(self):
        return self.nazwa


class Strazak(models.Model):
    STOPNIE = [
        ('strazak', 'Strażak'),
        ('strazak-ratownik', 'Strażak-ratownik'),
        ('kierowca', 'Kierowca'),
        ('dowodca', 'Dowódca'),
        ('naczelnik', 'Naczelnik'),
    ]

    imie = models.CharField(max_length=30)
    nazwisko = models.CharField(max_length=30)
    stopien = models.CharField(max_length=30, choices=STOPNIE, default='strazak')
    data_badan = models.DateField(verbose_name="Data ważności badań")
    @property
    def dni_do_badan(self):
        if self.data_badan:
            
            return (self.data_badan - date.today()).days
        return None

    class Meta:
        verbose_name = "Strażak"
        verbose_name_plural = "Strażacy"

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    def suma_godzin(self):
        from datetime import timedelta, date
        
        obecny_rok = date.today().year
        
        akcje = self.udzial_w_akcjach.filter(data_godzina_wyjazdu__year=obecny_rok)
        
        laczny_czas = timedelta()

        for akcja in akcje:
            if akcja.data_godzina_powrotu and akcja.data_godzina_wyjazdu:
                laczny_czas += akcja.data_godzina_powrotu - akcja.data_godzina_wyjazdu
        
        sekundy = laczny_czas.total_seconds()
        godziny = int(sekundy // 3600)
        minuty = int((sekundy % 3600) // 60)
        
        return f"{godziny}h {minuty}min (w {obecny_rok}r.)"
    
class Pojazd(models.Model):
    nazwa = models.CharField(max_length=50) 
    oznaczenie = models.CharField(max_length=20) 
    numer_operacyjny = models.CharField(max_length=20, unique=True) 
    sprawny = models.BooleanField(default=True)
    data_przegladu = models.DateField(null=True, blank=True, verbose_name="Data przeglądu")
    data_oc = models.DateField(null=True, blank=True, verbose_name="Data ubezpieczenia OC")


    @property
    def dni_do_przegladu(self):
        if self.data_przegladu:
            return (self.data_przegladu - date.today()).days 
        return None

    @property
    def dni_do_oc(self):
        if self.data_oc:
            return (self.data_oc - date.today()).days
        return None

    class Meta:
        verbose_name = "Pojazd i Łódź"
        verbose_name_plural = "Pojazdy i Łodzie"

    def __str__(self):
        return f"{self.numer_operacyjny} - {self.nazwa}"
    
    def liczba_wyjazdow_rok(self):
        from datetime import date
        obecny_rok = date.today().year
        return self.akcje.filter(data_godzina_wyjazdu__year=obecny_rok).count()
    
class Akcja(models.Model):
    RODZAJE = [
        ('pozar', 'Pożar'),
        ('wypadek', 'Wypadek'),
        ('miejscowe', 'Miejscowe Zagrożenie'),
        ('falszywy', 'Alarm Fałszywy'),
        ('zabezpieczenie', 'Zabezpieczenie Eventu'),
        ('gospodarczy', 'Wyjazd Gospodarczy'),
    ]

    numer_zdarzenia = models.CharField(max_length=20, unique=True)
    rodzaj = models.CharField(max_length=20, choices=RODZAJE)
    miejsce = models.CharField(max_length=200)
    data_godzina_wyjazdu = models.DateTimeField()
    opis = models.TextField(blank=True)
    data_godzina_powrotu = models.DateTimeField(null=True, blank=True)
    
    dowodca = models.ForeignKey(Strazak, on_delete=models.SET_NULL, null=True, related_name='prowadzone_akcje')
    pojazdy = models.ManyToManyField(Pojazd, related_name='akcje', verbose_name="Pojazdy biorące udział")
    ratownicy = models.ManyToManyField(Strazak, related_name='udzial_w_akcjach', verbose_name="Skład osobowy")

    class Meta:
        verbose_name = "Akcja Ratownicza"
        verbose_name_plural = "Akcje Ratownicze"

    def __str__(self):
        return f"Akcja {self.numer_zdarzenia} - {self.miejsce}"
    
    def czas_trwania(self):
        if self.data_godzina_powrotu and self.data_godzina_wyjazdu:
            roznica = self.data_godzina_powrotu - self.data_godzina_wyjazdu
            sekundy = roznica.total_seconds()
            godziny = int(sekundy // 3600)
            minuty = int((sekundy % 3600) // 60)
            return f"{godziny}h {minuty}min"
    

class Wydarzenie(models.Model):
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa wydarzenia")
    data = models.DateField(verbose_name="Data wydarzenia")
    notatki = models.TextField(blank=True, verbose_name="Notatki")


    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"

    def __str__(self):
        return self.nazwa

