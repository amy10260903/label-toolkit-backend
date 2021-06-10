from django.db import models

# Create your models here.

class Recording(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    category = models.CharField(max_length=64, null=False, default='origin', help_text='資料庫類別')
    filename = models.CharField(null=False, max_length=250, help_text='錄音檔名')
    fingerprinted = models.BooleanField(null=True, default=False, help_text='指紋識別狀態')
    file_sha1 = models.CharField(max_length=160, null=False, help_text='')
    total_hashes = models.IntegerField(null=False, default=0, help_text='指紋總數')
    date_created = models.DateTimeField(auto_now_add=True, help_text='建立時間')
    date_modified = models.DateTimeField(auto_now=True, help_text='更新時間')

    def __str__(self):
        return self.filename

class Fingerprint(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    recording = models.ForeignKey(Recording, related_name='recording', null=False, on_delete=models.CASCADE, help_text='音檔id')
    hash = models.CharField(max_length=80, null=False, help_text='指紋加密')
    offset = models.IntegerField(null=False, help_text='指紋起始點')
    date_created = models.DateTimeField(auto_now_add=True, help_text='建立時間')
    date_modified = models.DateTimeField(auto_now=True, help_text='更新時間')

    class Meta:
        unique_together = ('recording', 'hash', 'offset')

class Request(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    ip_address = models. GenericIPAddressField()
    query_name = models.CharField(null=False, max_length=250, help_text='檢索檔名')
    query_dataset = models.CharField(max_length=64, null=False, default='origin', help_text='檢索資料庫類別')
    date_created = models.DateTimeField(auto_now_add=True, help_text='建立時間')
    date_modified = models.DateTimeField(auto_now=True, help_text='更新時間')
    matched_result = models.JSONField(null=True, help_text='配對結果')

class Userlog(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    request = models.ForeignKey(Request, related_name='request', default=0, on_delete=models.SET_DEFAULT, help_text='要求id')
    filename = models.CharField(null=False, max_length=250, help_text='錄音檔名')
    labeled_time = models.DurationField(null=False, help_text='標記時間')
