from django.db import models
from django.contrib.auth.models import User

class Personnel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_personnel',
                             on_delete=models.PROTECT)
    telephone = models.PositiveIntegerField()
    genre = models.CharField(max_length = 20)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.first_name}"

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
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    genre = models.CharField(max_length = 20,null=True,blank=True)
    date_naissance = models.CharField(max_length=20, null=True, blank=True)
    classe = models.ForeignKey("Classe", null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.first_name