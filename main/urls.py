from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main.views import \
    FingerprintViewSet, \
    OptionViewSet

router = DefaultRouter()
router.register(r'fingerprint', FingerprintViewSet, basename='fingerprint')
router.register(r'option', OptionViewSet, basename='option')

urlpatterns = [
    path('', include(router.urls)),
]