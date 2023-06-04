from django.urls import path, include
from rest_framework import routers
from .views import *

from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView
router = routers.DefaultRouter()
router.register("groups", GroupViewSet)
router.register("users", UserViewSet)
router.register("cycles", CycleViewSet)
router.register("classes", ClasseViewSet)
router.register("cours", CourViewSet)
router.register("formules", FormulesViewSet)
router.register("epreuves-types", EpreuvesTypesViewSet)
router.register("chapitres", ChapitreViewSet)
router.register("exercices", ExerciceViewSet)
router.register("eleves", EleveViewSet)
router.register("niveaux", NiveauViewSet)
router.register("professeurs", ProfesseurViewSet)
router.register("reponseEleves", ReponseEleveViewSet)
router.register("sections", SectionViewSet)
router.register("cours-speciaux", CoursSpeciauxViewSet)
router.register("chapitres-csp", ChapitresCSPViewSet)
router.register("exercices-csp", ExerciceCSPViewSet)
router.register("reponses-csp", ReponseCSPViewSet)
router.register("abonnements", AbonnementsViewSet)
router.register("categories", CategorieViewSet)
router.register("parents", ParentViewSet)


urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('api_auth', include('rest_framework.urls')),
]
