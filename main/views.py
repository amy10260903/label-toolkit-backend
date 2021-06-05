from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.cache import cache
from django_redis import get_redis_connection
import json

from main.method import recognize
from main.method.encoder import MyEncoder

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
        params = {'thsld': 18, 'fan': 40}
        is_stream = True
        recordings = recognize(file, request.data['category'], params, is_stream)
        recordings = recordings._replace(
                        matched_result=[obj._asdict() for obj in recordings.matched_result],
                        event_name=request.data['filename'])

        if recordings:
            return Response(json.dumps(recordings._asdict(), cls=MyEncoder), status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class OptionViewSet(mixins.CreateModelMixin,
                    GenericViewSet):
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        response = {}
        default = get_redis_connection('default')
        response['results'] = sorted(default.smembers('dataset'))
        # if cache.has_key('dataset'):
        #     response['dataset'] = cache.get('dataset')

        return Response(response, status=status.HTTP_200_OK)
