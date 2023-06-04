from django.db import models
from django.contrib.auth.models import User


class Professeur(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_professeur',
                             on_delete=models.PROTECT)
    telephone = models.PositiveIntegerField()
    genre = models.CharField(max_length = 20)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.first_name}"

class Parent(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_parent',
                             on_delete=models.PROTECT)
    telephone = models.PositiveIntegerField()
    genre = models.CharField(max_length = 20, null=True, blank=True)
    date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"{self.user.username} {self.telephone}"

class Eleve(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_eleve',
                             on_delete=models.PROTECT, null=True, blank=True)
    parent = models.ForeignKey(Parent, related_name='user_parent',
                             on_delete=models.PROTECT, null=True, blank=True)
    pin = models.CharField(max_length=4, null=True,blank=True)
    telephone = models.PositiveIntegerField(null=True,blank=True)
    date = models.DateField(auto_now_add = True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    genre = models.CharField(max_length = 20,null=True,blank=True)
    date_naissance = models.CharField(max_length=20, null=True, blank=True)
    ecole = models.CharField(max_length=150, null=True)
    classe = models.ForeignKey("Classe", null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if(self.parent != None and self.pin==None):
            raise Exception("Pin required if parent")
        else:
            super(Eleve, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user) if self.user else str(self.parent)

    def complete(self):
        return (
            bool(self.first_name) and
            bool(self.last_name) and
            bool(self.genre) and
            bool(self.date_naissance) and
            bool(self.ecole) and
            bool(self.classe)
        ) if self.parent else (
            bool(self.user.first_name) and
            bool(self.user.last_name) and
            bool(self.genre) and
            bool(self.date_naissance) and
            bool(self.ecole) and
            bool(self.classe)
        )

    class Meta:
        unique_together = "parent", "pin",

class Niveau(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_niveau',
                             on_delete=models.PROTECT, editable=False,
                             null=True, blank=True)
    nom = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom}"

class Cycle(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_cycle',
                             on_delete=models.PROTECT, editable=False)
    niveau = models.ForeignKey(Niveau, on_delete=models.PROTECT)
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
    cycle = models.ForeignKey(Cycle, on_delete=models.PROTECT, null = True)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, null = True)
    nom = models.CharField(max_length=50)
    user = models.ForeignKey(User, related_name='user_classe',
                             on_delete=models.PROTECT, editable=False, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom}--{self.niveau}--{self.section}"


class Cour(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_cour',
                             on_delete=models.PROTECT, editable=False, null=True, blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT)
    professeur = models.ForeignKey(Professeur,on_delete = models.PROTECT, null=True, blank=True)
    nom = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    validated = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {str(self.classe)}"

class Formules(models.Model):
    id = models.BigAutoField(primary_key=True)
    cour = models.ForeignKey(Cour, on_delete=models.PROTECT)
    formules = models.TextField(null=True, blank=True)
    pdf = models.FileField(upload_to="epreuves/",null=True,blank=True)
    date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cour.nom}"

class EpreuvesTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    cour = models.ForeignKey(Cour, on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    pdf = models.FileField(upload_to="epreuves/",null=True,blank=True)
    date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cour.nom}"


class Chapitre(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_chapitre',
                             on_delete=models.PROTECT, editable=False, null=True, blank=True)
    cour = models.ForeignKey(Cour, on_delete=models.PROTECT)
    note = models.TextField()
    nom = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    valide_par = models.ForeignKey(
                                    User, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name="validatedUser")
    validated = models.BooleanField(default=False)
    valide_le=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.nom}"

class Exercice(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_exercice',
                             on_delete=models.PROTECT, editable=False)
    chapitre = models.ForeignKey(Chapitre, on_delete=models.PROTECT)
    question = models.TextField()
    detail = models.TextField()
    reponse = models.CharField(max_length = 100)
    mauvaise_reponse1 = models.CharField(max_length = 100)
    mauvaise_reponse2 = models.CharField(max_length = 100)
    mauvaise_reponse3 = models.CharField(max_length = 100)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.chapitre}"

class Correction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_correction',
                             on_delete=models.PROTECT, editable=False)
    exercice = models.ForeignKey(Exercice, on_delete=models.PROTECT)
    detail_response = models.TextField()
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.exercice}"

class ReponseEleve(models.Model):
    id = models.BigAutoField(primary_key = True)
    eleve = models.ForeignKey(Eleve, related_name='eleve_reponse',null=True,blank=True,
                             on_delete=models.PROTECT, editable=False)
    exercice = models.ForeignKey(Exercice, on_delete=models.PROTECT)
    reponse = models.CharField(max_length = 100)
    trouve = models.BooleanField(default = False, editable=False)
    date = models.DateField(auto_now_add = True)

#cours speciaux----------------------------------------------------------------------

class Categorie(models.Model):
    id=models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=150)

    def __str__(self):
        return self.nom

class CoursSpeciaux(models.Model):
    id=models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=150)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    valide_par = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    validated = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    modifie_le = models.DateTimeField(auto_now_add=True)

class ChapitresCSP(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_chapitre_cs',
                             on_delete=models.PROTECT, editable=False, null=True, blank=True)
    cour = models.ForeignKey(CoursSpeciaux, on_delete=models.PROTECT)
    nom = models.CharField(max_length=255)
    note = models.TextField()
    date = models.DateField(auto_now_add=True)
    valide_par = models.ForeignKey(User, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name="validatebyUser_cs")
    validated = models.BooleanField(default=False)
    valide_le=models.DateTimeField(null=True,blank=True)

class ExerciceCSP(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='user_exercicesp',
                             on_delete=models.PROTECT, editable=False)
    chapitre = models.ForeignKey(ChapitresCSP, on_delete=models.PROTECT)
    question = models.TextField()
    detail = models.TextField()
    reponse = models.CharField(max_length = 100)
    mauvaise_reponse1 = models.CharField(max_length = 100)
    mauvaise_reponse2 = models.CharField(max_length = 100)
    mauvaise_reponse3 = models.CharField(max_length = 100)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"{self.chapitre}"


class ReponseCSP(models.Model):
    id = models.BigAutoField(primary_key = True)
    user = models.ForeignKey(User, related_name='response_usersp',null=True,blank=True,
                             on_delete=models.PROTECT, editable=False)
    exercice = models.ForeignKey(ExerciceCSP, on_delete=models.PROTECT)
    reponse = models.CharField(max_length = 100)
    trouve = models.BooleanField(default = False, editable=False)
    date = models.DateField(auto_now_add = True)

TYPE_ABONEMENT = (("simple","Simple"),("special","Special"))

class Abonnements(models.Model):
    id=models.BigAutoField(primary_key=True)
    eleve=models.ForeignKey(Eleve, on_delete=models.CASCADE)
    classe=models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)
    cours=models.ForeignKey(CoursSpeciaux, on_delete=models.CASCADE, null=True, blank=True)
    type_abonement = models.CharField(max_length=20, null=True, choices=TYPE_ABONEMENT)
    date_abonement = models.DateTimeField(auto_now=True)
    mode_payement = models.CharField(max_length=30)
    id_transaction = models.CharField(max_length=150)
    valide = models.BooleanField(default=False)


