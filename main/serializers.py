from rest_framework import serializers
from main.models import \
    Recording,\
    Fingerprint,\
    RecordingWithNR,\
    FingerprintWithNR

class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = "__all__"

class FingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = "__all__"

class RecordingWithNRSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordingWithNR
        fields = "__all__"

class FingerprintWithNRSerializer(serializers.ModelSerializer):
    class Meta:
        model = FingerprintWithNR
        fields = "__all__"