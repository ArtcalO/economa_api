from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from django.db import transaction
from .serializers import *
from .models import *
from datetime import datetime, timedelta
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum


class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer


class GroupViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Group.objects.all()
	serializer_class = GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all().order_by('-id')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	# modification mot de passe

	@transaction.atomic()
	def update(self, request, pk):
		user = self.get_object()
		print(user)
		data = request.data
		username = data.get('username')
		first_name = data.get('first_name')
		last_name = data.get('last_name')
		nouv_password = data.get('nouv_password')
		anc_password = data.get('anc_password')
		if user.check_password(anc_password):
			print("checked")
			user.username = username
			user.first_name = first_name
			user.last_name = last_name
			user.set_password(nouv_password)
			user.save()
			return Response({"status": "Utilisateur modifié avec success"}, 201)
		return Response({"status": "Ancien mot de passe incorrect"}, 400)


	@action(methods=["POST"], detail=False, url_name=r"register",url_path=r"register",permission_classes=[AllowAny])
	def register(self, request):
		telephone = request.data.get('telephone')
		password=request.data.get('password')
		user = User(username=telephone)
		user.set_password(password)
		try:
			user.save()
			if(request.data.get("parent")):
				parent = Parent(
					user=user,
					telephone=telephone
				)
				group = Group.objects.get_or_create(name='Parent')
				user.groups.add(group[0])
				parent.save()
			else:
				eleve:Eleve = Eleve(
					user = user,
					telephone = telephone
				)
				group = Group.objects.get_or_create(name='Eleve')
				user.groups.add(group[0])
				eleve.save()
		except Exception as e:
			print(str(e))
			return Response({"details":str(e)},500)
		return Response(201)

class ParentViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ParentSerializer
	queryset = Parent.objects.all().order_by('-id')

	@action(methods=["POST"], detail=True, url_name=r"add-child",url_path=r"add-child")
	def addChild(self, request, pk):
		parent=self.get_object()
		data = request.data
		first_name = request.data["first_name"]
		last_name = request.data["last_name"]
		genre = request.data["genre"]
		date_naissance = request.data["date_naissance"]
		classe:Classe=Classe.objects.get(id=request.data["classe"])
		pin = request.data["pin"]
		eleve:Eleve = Eleve(
			first_name=first_name,
			last_name=last_name,
			genre=genre,
			date_naissance=date_naissance,
			classe=classe,
			pin=pin,
			parent=parent
			)
		eleve.save()
		serializer = EleveSerializer(
			eleve, many=False, context={"request": request})
		return Response(serializer.data, 201)

class ProfesseurViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ProfesseurSerializer
	queryset = Professeur.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = []
	search_fields = []

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		telephone = serializer.validated_data['telephone']
		genre = serializer.validated_data['genre']
		user_serial = serializer.validated_data['user']
		user = User(
			username=user_serial['username'],
			first_name=user_serial['first_name'],
			last_name=user_serial['last_name'],
		)
		user.set_password(serializer.validated_data['user']['password'])
		professeur:Professeur = Professeur(
			user = user,
			telephone = telephone,
			genre = genre
			)
		user.save()
		group = Group.objects.get_or_create(name='Professeur')
		user.groups.add(group[0])
		user.save()
		professeur.save()
		serializer = ProfesseurSerializer(
			professeur, many=False, context={"request": request})
		return Response(serializer.data, 201)

class EleveViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = EleveSerializer
	queryset = Eleve.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {"parent":['exact'],"user":['exact']}
	search_fields = ["parent","user"]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		telephone = serializer.validated_data['telephone']
		genre = serializer.validated_data['genre']
		user_serial = serializer.validated_data['user']
		user = User(
			username=user_serial['username'],
			first_name=user_serial['first_name'],
			last_name=user_serial['last_name']
		)
		user.set_password(serializer.validated_data['user']['password'])
		eleve:Eleve = Eleve(
			user = user,
			telephone = telephone,
			genre = genre
			)
		user.save()
		group = Group.objects.get_or_create(name='Eleve')
		user.groups.add(group[0])
		user.save()
		eleve.save()
		serializer = EleveSerializer(
			eleve, many=False, context={"request": request})
		return Response(serializer.data, 201)

	@action(methods=["POST"], detail=True, url_name=r"completer-profil",url_path=r"completer-profil",permission_classes=[AllowAny])
	def modifierProfil(self, request, pk):
		eleve = self.get_object()
		data = request.data

		# if self.context['request'].user != user :
		# 	raise Exception("You can only update your own account")

		first_name = data["first_name"]
		last_name = data["last_name"]
		genre = data["genre"]
		date_naissance = data["date_naissance"]
		classe:Classe = Classe.objects.get(id = data["classe"])
		ecole = data["ecole"]

		if first_name : eleve.first_name = first_name
		if last_name : eleve.last_name = last_name
		if genre : eleve.genre = genre
		if date_naissance : eleve.date_naissance = date_naissance
		if classe : eleve.classe = classe
		if ecole : eleve.ecole = ecole

		if(eleve.user):
			user=eleve.user
			user.first_name=first_name
			user.last_name=last_name
			user.save()
		eleve.save()

		return Response(200)

class CycleViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = CycleSerializer
	queryset = Cycle.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = [
		'nom',
		'niveau__nom'
	]
	search_fields = [
		'nom',
		'niveau__nom'
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		nom = data['nom']
		niveau = data['niveau']
		user = request.user
		cycle: Cycle = Cycle(
			nom=nom,
			niveau=niveau,
			user=user
		)
		cycle.save()
		serializer = NiveauSerializer(
			cycle, many=False, context={"request": request})
		return Response(serializer.data, 201)

class NiveauViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = NiveauSerializer
	queryset = Niveau.objects.all().order_by('id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = [
		'nom'
	]
	search_fields = [
		'nom'
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		nom = data['nom']
		user = request.user
		niveau: Niveau = Niveau(
			nom=nom,
			user=user
		)
		niveau.save()
		serializer = NiveauSerializer(
			niveau, many=False, context={"request": request})
		return Response(serializer.data, 201)


class SectionViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = SectionSerializer
	queryset = Section.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = [
		'nom',
		'niveau__nom'
	]
	search_fields = [
		'nom',
		'niveau__nom'
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		nom = data['nom']
		niveau: Niveau = data['niveau']
		user = request.user
		section: Section = Section(
			nom=nom,
			niveau=niveau,
			user=user
		)
		section.save()
		serializer = SectionSerializer(
			section, many=False, context={"request": request})
		return Response(serializer.data, 201)


class ClasseViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ClasseSerializer
	queryset = Classe.objects.all().order_by('id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = [
		'niveau',
		'section',
		'id'
	]
	search_fields = [
		'niveau__nom',
		'section__nom',
		'nom'
	]

	# @transaction.atomic()
	# def create(self, request):
	# 	serializer = self.get_serializer(data=request.data)
	# 	serializer.is_valid(raise_exception=True)
	# 	data = serializer.validated_data
	# 	nom = data['nom']
	# 	section:Section = data['section']
	# 	cycle:Cycle = data['cycle']
	# 	user = request.user
	# 	classe: Classe = Classe(
	# 			nom=nom,
	# 			user=user
	# 		)
	# 	if section:
	# 		niveau:Niveau = section.niveau
	# 		classe.niveau = niveau
	# 		classe.section = section
	# 		classe.save()
	# 	if cycle:
	# 		niveau:Niveau = cycle.niveau
	# 		classe.niveau = niveau
	# 		classe.cycle = cycle
	# 		classe.save()
	# 	serializer = ClasseSerializer(
	# 		classe, many=False, context={"request": request})
	# 	return Response(serializer.data, 201)


class CourViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = CourSerializer
	queryset = Cour.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'classe': ['exact'],
		'professeur':['exact'],
		'validated':['exact']
	}

	search_fields = [
		'classe__cycle__nom'
		'classe__section__nom'
		'nom'
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		nom = data['nom']
		description = data['description']
		classe: Classe = data['classe']
		professeur: Professeur = data['professeur']
		user = request.user
		cour: Cour = Cour(
			nom=nom,
			classe=classe,
			description=description,
			professeur=professeur,
			user=user
		)
		cour.save()
		serializer = CourSerializer(
			cour, many=False, context={"request": request})
		return Response(serializer.data, 201)

class FormulesViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = FormulesSerializer
	queryset = Formules.objects.all().order_by('-id')

class EpreuvesTypesViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = EpreuvesTypesSerializer
	queryset = EpreuvesTypes.objects.all().order_by('-id')


class ChapitreViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ChapitreSerializer
	queryset = Chapitre.objects.all().order_by('id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'cour': ['exact'],
	 	}
	search_fields = [
		'cour__nom'
		'cour__classe__nom'
		'nom'
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		nom = data['nom']
		note = data['note']
		cour: Cour = data['cour']
		user = request.user
		chapitre: Chapitre = Chapitre(
			nom=nom,
			cour=cour,
			note=note,
			user=user
		)
		chapitre.save()
		serializer = ChapitreSerializer(
			chapitre, many=False, context={"request": request})
		return Response(serializer.data, 201)

class ExerciceViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ExerciceSerializer
	queryset = Exercice.objects.all().order_by('id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'chapitre': ['exact'],
	}
	search_fields = [
		'chapitre__nom',
		'chapitre__cour__nom',
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		user = request.user
		chapitre: Chapitre = data['chapitre']
		question = data['question']
		detail = data['detail']
		reponse = data['reponse']
		mauvaise_reponse1 = data['mauvaise_reponse1']
		mauvaise_reponse2 = data['mauvaise_reponse2']
		mauvaise_reponse3 = data['mauvaise_reponse3']
		exercice: Exercice = Exercice(
			user=user,
			chapitre=chapitre,
			question = question,
			detail = detail,
			reponse = reponse,
			mauvaise_reponse1 = mauvaise_reponse1,
			mauvaise_reponse2 = mauvaise_reponse2,
			mauvaise_reponse3 = mauvaise_reponse3
		)
		exercice.save()
		serializer = ExerciceSerializer(
			exercice, many=False, context={"request": request})
		return Response(serializer.data, 201)

class ReponseEleveViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ReponseEleveSerializer
	queryset = ReponseEleve.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = []
	search_fields = []

	@transaction.atomic()
	def create(self, request):
		data = request.data
		reponses = data.get("reponses")
		eleve = Eleve.objects.get(id=data.get("eleve"))
		correction_eleve=[]
		user = request.user
		for el in reponses:
			exercice:Exercice=Exercice.objects.get(id=el.get("q_id"))
			reponse = el.get("resp")
			trouve = False
			if exercice.reponse == reponse:
				trouve = True
			reponseEleve= ReponseEleve(
				eleve=eleve,
				exercice = exercice,
			)
			reponseEleve.reponse = reponse
			reponseEleve.trouve = trouve
			reponseEleve.save()
			correction_eleve.append(reponseEleve)
		serializer = ReponseEleveSerializer(correction_eleve, many=True).data
		return Response(serializer, 201)


class CoursSpeciauxViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = CoursSpeciauxSerializer
	queryset = CoursSpeciaux.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {'professeur':['exact'],'categorie':['exact']}
	search_fields = []
	
class ChapitresCSPViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ChapitresCSPSerializer
	queryset = ChapitresCSP.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'cour': ['exact'],
	 	}
	search_fields = []


class ExerciceCSPViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ExerciceCSPSerializer
	queryset = ExerciceCSP.objects.all().order_by('id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'chapitre': ['exact'],
	}
	search_fields = [
		'chapitre__nom',
		'chapitre__cour__nom',
	]

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		user = request.user
		chapitre: ChapitresCSP = data['chapitre']
		question = data['question']
		detail = data['detail']
		reponse = data['reponse']
		mauvaise_reponse1 = data['mauvaise_reponse1']
		mauvaise_reponse2 = data['mauvaise_reponse2']
		mauvaise_reponse3 = data['mauvaise_reponse3']
		exercice: ExerciceCSP = ExerciceCSP(
			user=user,
			chapitre=chapitre,
			question = question,
			detail = detail,
			reponse = reponse,
			mauvaise_reponse1 = mauvaise_reponse1,
			mauvaise_reponse2 = mauvaise_reponse2,
			mauvaise_reponse3 = mauvaise_reponse3
		)
		exercice.save()
		serializer = ExerciceCSPSerializer(
			exercice, many=False, context={"request": request})
		return Response(serializer.data, 201)

class ReponseCSPViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ReponseCSPSerializer
	queryset = ReponseEleve.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = []
	search_fields = []

	@transaction.atomic()
	def create(self, request):
		data = request.data
		reponses = data.get("reponses")
		correction_eleve=[]
		user = request.user
		for el in reponses:
			exercice:ExerciceCSP=ExerciceCSP.objects.get(id=el.get("q_id"))
			reponse = el.get("resp")
			trouve = False
			if exercice.reponse == reponse:
				trouve = True
			reponseEleve= ReponseCSP(
				user=request.user,
				exercice = exercice,
			)
			reponseEleve.reponse = reponse
			reponseEleve.trouve = trouve
			reponseEleve.save()
			correction_eleve.append(reponseEleve)
		serializer = ReponseCSPSerializer(correction_eleve, many=True).data
		return Response(serializer, 201)


class AbonnementsViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = AbonnementsSerializer
	queryset = Abonnements.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = []
	search_fields = []

class CategorieViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = CategorieSerializer
	queryset = Categorie.objects.all().order_by('-id')
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = []
	search_fields = []