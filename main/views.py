from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.cache import cache
from django_redis import get_redis_connection
import pickle

from main.models import Recording, Fingerprint
from main.serializers import RecordingSerializer, FingerprintSerializer

from main.dejavu import recognize
from main.dejavu.logic.recognizer.file_recognizer import FileRecognizer

# Create your views here.
class FingerprintViewSet(mixins.CreateModelMixin,
                         GenericViewSet):
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        print(f"request >> {request.data}")
        errors = {}
        if 'file' not in request.data:
            errors['file'] = ["沒有上傳檔案"]
        if 'category' not in request.data:
            errors['category'] = ["category 不能為空"]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        file = request.data['file']
        songs = recognize(FileRecognizer, file)

        if songs:
            return Response(songs, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class OptionViewSet(mixins.CreateModelMixin,
                    GenericViewSet):
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        response = {}
        default = get_redis_connection('default')
        response['results'] = default.smembers('dataset')
        # if cache.has_key('dataset'):
        #     response['dataset'] = cache.get('dataset')

        return Response(response, status=status.HTTP_200_OK)
