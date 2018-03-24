from django.db import models
from utils.models import BaseModel
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime


# Create your models here.

class UserInfo(BaseModel, AbstractUser):
    class Meta:
        db_table = "tt_users"

    def __default(self,obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            raise TypeError('%r is not JSON serializable' % obj)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]),default=self.__default)


class AreaInfo(models.Model):
    title = models.CharField(max_length=20)
    aParent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        db_table = 'tt_area'


class AddrInfo(BaseModel):
    receiver = models.CharField(max_length=10)
    province = models.ForeignKey('AreaInfo', related_name='province')
    city = models.ForeignKey('AreaInfo', related_name='city')
    district = models.ForeignKey('AreaInfo', related_name='district')
    addr = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=11)
    isDefault = models.BooleanField(default=False)
    user = models.ForeignKey('UserInfo')

    class Meta:
        db_table = 'AddrInfo'
