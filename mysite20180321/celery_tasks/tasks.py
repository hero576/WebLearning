from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from celery import Celery
from tt_goods.admin import *
from django.shortcuts import render

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


@app.task
def generate_index():
    category_list = GoodsCategory.objects.all()
    banner_list = IndexGoodsBanner.objects.all().order_by("index")
    adv_list = IndexPromotionBanner.objects.all().order_by("index")

    for category in category_list:
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0).order_by(
            "index")[0:3]
        category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1).order_by(
            "index")[0:4]
    context = {
        "title": "首页",
        "category_list": category_list,
        "banner_list": banner_list,
        "adv_list": adv_list,
    }
    response = render(None, "index.html", context)
    with open(settings.GENERATE_DIRS+"index.html", 'w') as f:
        f.write(response.content.decode())
