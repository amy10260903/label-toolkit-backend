from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.cache import cache
from django_redis import get_redis_connection

from types import SimpleNamespace
import json
import datetime
import os

from main.method import recognize
from main.method.encoder import MyEncoder
from main.models import Request, Userlog

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

        req = Request.objects.create(
            ip_address=request.META.get('REMOTE_ADDR'),
            query_name=request.data['event'],
            query_dataset=request.data['category'],
        )
        # file = request.data['file']
        # is_stream = True
        # params = {'thsld': 18, 'fan': 40}
        params = {'thsld': 24, 'fan': 20}
        is_stream = False
        file = os.path.join('static', 'assets', 'dataset', 'event', f"{request.data['event']}.mp3")
        recordings = recognize(file, request.data['category'], params, is_stream)
        recordings = recordings._replace(
                        matched_result=[obj._asdict() for obj in recordings.matched_result],
                        event_name=request.data['event'])
                        # event_name=file.name)
        if recordings:
            response = {}
            response['results'] = json.dumps(recordings._asdict(), cls=MyEncoder)
            response['request_id'] = req.id
            req.matched_result = response['results']
            req.save()
            # tmp = json.loads(req.matched_result, object_hook=lambda d: SimpleNamespace(**d))
            # print(tmp.event_name)
            return Response(response, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class UserlogViewSet(mixins.CreateModelMixin,
                     GenericViewSet):
    http_method_names = ["post"]
    def create(self, request, *args, **kwargs):
        errors = {}
        if 'request_id' not in request.data:
            errors['request_id'] = ["request_id 不能為空"]
        if 'filename' not in request.data:
            errors['filename'] = ["filename 不能為空"]
        if 'time' not in request.data:
            errors['time'] = ["time 不能為空"]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        print(request.data)
        req = Request.objects.filter(id=request.data['request_id']).first()
        log = Userlog.objects.create(
            request=req,
            filename=request.data['filename'],
            labeled_time=datetime.timedelta(days=-1, seconds=request.data['time']),
        )
        if log:
            # print(log.labeled_time)
            return Response(status=status.HTTP_200_OK)

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
