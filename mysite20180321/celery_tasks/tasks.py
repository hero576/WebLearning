from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from celery import Celery


app=Celery("celery_tasks.tasks",broker="redis://127.0.0.1:6379/5",)

@app.task
def send_user_active(userid,email):
    # 将账号信息进行加密
    serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 2)
    value = serializer.dumps({"id":userid })  # 返回bytes
    value = value.decode()

    # 向用户发送邮件
    msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
    send_mail('GM平台激活', '', settings.EMAIL_FROM, [email], html_message=msg)
