from django.urls import path, include
from rest_framework import routers
from .views import *

from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView
router = routers.DefaultRouter()
router.register("groups", GroupViewSet)
router.register("users", UserViewSet)
router.register("personnels", PersonnelViewSet)
router.register("niveaux", NiveauViewSet)
router.register("sections", SectionViewSet)
router.register("classes", ClasseViewSet)
router.register("eleves", EleveViewSet)
router.register("entrees", EntreeViewSet)
router.register("sorties", SortieViewSet)
router.register("det-ent-locations", DetailsEntreeLocationViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('api_auth', include('rest_framework.urls')),
]
