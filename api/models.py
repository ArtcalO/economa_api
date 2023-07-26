from django.db import models
from django.contrib.auth.models import User

class TYPES_ENTREES(models.IntegerChoices):
    AUTRES = 0
    BUDGET_MINISTRE = 1
    LOCATION_SALLE = 2
    LOCATION_TERRAIN = 3
    LOCATION_CHAMP = 4
    LOCATION_ATELIER = 5
    PAIEMENT_MINERVAL = 6

class TYPES_SORTIES(models.IntegerChoices):
    AUTRES = 0
    RATION = 1
    MAIN_OEUVRES = 2
    EQUIPEMENTS_ATELIERS = 3
    EVENEMENTS = 4

class Personnel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_personnel',
                             on_delete=models.PROTECT)
    telephone = models.PositiveIntegerField()
    genre = models.CharField(max_length = 20)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.telephone} {self.genre}"

class Niveau(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_niveau',
                             on_delete=models.PROTECT, editable=False,
                             null=True, blank=True)
    nom = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom}"


class Section(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_section',null=True,blank=True,
                             on_delete=models.PROTECT, editable=False)
    niveau = models.ForeignKey(Niveau, on_delete=models.PROTECT)
    nom = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom}"


class Classe(models.Model):
    id = models.BigAutoField(primary_key=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, null = True)
    nom = models.CharField(max_length=50)
    user = models.ForeignKey(User, related_name='user_classe',
                             on_delete=models.PROTECT, editable=False, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom}--{self.niveau}--{self.section}"

class Eleve(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=150, null=True, blank=True)
    prenom = models.CharField(max_length=150, null=True, blank=True)
    genre = models.CharField(max_length = 20,null=True,blank=True)
    date_naissance = models.CharField(max_length=20, null=True, blank=True)
    classe = models.ForeignKey("Classe", null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.nom

class Entree(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    type_entree = models.IntegerField(default=-1, choices=TYPES_ENTREES.choices)
    montant = models.CharField(max_length=150, null=True, blank=True)
    details = models.CharField(max_length = 20,null=True,blank=True)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.details

class DetailsEntreeLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    entree = models.ForeignKey(Entree, editable=False, on_delete=models.CASCADE)
    nom = models.CharField(max_length=150, null=True, blank=True)
    prenom = models.CharField(max_length=150, null=True, blank=True)
    telephone = models.CharField(max_length = 20,null=True,blank=True)
    adresse = models.CharField(max_length=150, null=True, blank=True)
    cni = models.CharField(max_length=150, null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    date = models.DateTimeField(auto_now=True)


class Sortie(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    type_sortie = models.IntegerField(default=-1, choices=TYPES_SORTIES.choices)
    montant = models.CharField(max_length=150, null=True, blank=True)
    details = models.CharField(max_length = 20,null=True,blank=True)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.details