from django.db import models
import os
os.environ.update({"DJANGO_SETTINGS_MODULE": "mysite20180321.settings"})


class BaseModel(models.Model):
    # 添加时间
    add_date = models.DateTimeField(auto_now_add=True)
    # 最近修改时间
    update_date = models.DateTimeField(auto_now=True)
    # 逻辑删除
    isDelete = models.BooleanField(default=False)
    # 设置不创建
    class Meta:
        abstract=True
