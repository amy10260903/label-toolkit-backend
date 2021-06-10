from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.cache import cache
from django_redis import get_redis_connection
import json
import os

from main.method import recognize
from main.method.encoder import MyEncoder

# Create your views here.
class FingerprintViewSet(mixins.CreateModelMixin,
                         GenericViewSet):
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        print(f"request >> {request.data}")
        errors = {}
        # if 'file' not in request.data:
        #     errors['file'] = ["沒有上傳檔案"]
        if 'category' not in request.data:
            errors['category'] = ["category 不能為空"]
        if 'event' not in request.data:
            errors['event'] = ["event 不能為空"]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # file = request.data['file']
        # is_stream = True
        # params = {'thsld': 18, 'fan': 40}
        params = {'thsld': 24, 'fan': 20}
        is_stream = False
        file = os.path.join('static', 'assets', 'dataset', 'event', f"{request.data['event']}.mp3")
        recordings = recognize(file, f"{request.data['category']}_54", params, is_stream)
        recordings = recordings._replace(
                        matched_result=[obj._asdict() for obj in recordings.matched_result],
                        event_name=request.data['event'])
                        # event_name=file.name)
        if recordings:
            response = {}
            response['results'] = json.dumps(recordings._asdict(), cls=MyEncoder)
            return Response(response, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class OptionViewSet(mixins.CreateModelMixin,
                    GenericViewSet):
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        response = {}
        default = get_redis_connection('default')
        options = {
            'dataset': sorted(default.smembers('dataset')),
            'event': sorted(default.smembers('event'))
        }
        response['results'] = json.dumps(options, cls=MyEncoder)
        # if cache.has_key('dataset'):
        #     response['dataset'] = cache.get('dataset')

        return Response(response, status=status.HTTP_200_OK)
