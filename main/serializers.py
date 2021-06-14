from rest_framework import serializers
from main.models import \
    Recording,\
    Fingerprint,\
    Userlog

class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = "__all__"

class FingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = "__all__"

class UserlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userlog
        fields = "__all__"