from django.db import models

class Sprzet(models.Model):
    
    nazwa = models.CharField(max_length=100) 
    producent = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    numer_inwentarzowy = models.CharField(max_length=30, unique=True)
    data_zakupu = models.DateField()
    sprawny = models.BooleanField(default=True) 

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

    class Meta:
        verbose_name = "Strażak"
        verbose_name_plural = "Strażacy"

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
class Pojazd(models.Model):
    nazwa = models.CharField(max_length=50) # np. Star 266, Jelcz
    oznaczenie = models.CharField(max_length=20) # np. GBA 2.5/16
    numer_operacyjny = models.CharField(max_length=20, unique=True) # np. 301[P]21
    sprawny = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pojazd i Łódź"
        verbose_name_plural = "Pojazdy i Łodzie"

    def __str__(self):
        return f"{self.numer_operacyjny} - {self.nazwa}"
    
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
    
    dowodca = models.ForeignKey(Strazak, on_delete=models.SET_NULL, null=True, related_name='prowadzone_akcje')
    pojazd = models.ForeignKey(Pojazd, on_delete=models.SET_NULL, null=True, verbose_name="Pojazd")
    ratownicy = models.ManyToManyField(Strazak, related_name='udzial_w_akcjach', verbose_name="Skład osobowy")

    class Meta:
        verbose_name = "Akcja Ratownicza"
        verbose_name_plural = "Akcje Ratownicze"

    def __str__(self):
        return f"Akcja {self.numer_zdarzenia} - {self.miejsce}"
    

