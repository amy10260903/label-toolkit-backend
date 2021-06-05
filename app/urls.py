from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from app.views import DemoView

# router = DefaultRouter()
# router.register(r'demo', DemoViewSet, basename='demo')

urlpatterns = [
    # path('', include(router.urls)),
    url(r'^$', DemoView.as_view(), name='demo'),
]