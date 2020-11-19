from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main.views import RecognizeViewSet

router = DefaultRouter()
router.register(r'recognize', RecognizeViewSet, basename='recognize')

urlpatterns = [
    path('', include(router.urls)),
]