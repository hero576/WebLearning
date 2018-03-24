from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
import re
from .models import UserInfo
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_user_active
from django.contrib.auth import login,logout,authenticate


# Create your views here.
class RegisterView(View):
    def get(self, request):
        """处理get请求，返回注册页面"""
        return render(request, "register.html",{"title":"注册"})

    def post(self, request):
        """处理post请求，进行注册验证"""
        dict = request.POST
        uname = dict.get("user_name")
        upwd = dict.get("pwd")
        cpwd = dict.get("cpwd")
        email = dict.get("email")
        allow = dict.get("allow")
        err_text = ""

        context = {'uname': uname, 'upwd': upwd, 'cpwd': cpwd, 'email': email, 'err_text': err_text,"title":"注册"}

        # 注册信息校验
        if not all([uname, upwd, cpwd, email]):
            context["err_text"] = "请输入完整信息"
            return render(request, "register.html", context)

        if len(uname) < 5 | len(uname) > 20:
            context["err_text"] = "用户名格式不正确，请重新输入"
            return render(request, "register.html", context)

        if len(upwd) < 8 | len(upwd) > 20:
            context["err_text"] = "密码格式不正确，请重新输入"
            return render(request, "register.html", context)

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context["err_text"] = "邮箱格式不正确，请重新输入"
            return render(request, "register.html", context)

        if not cpwd == upwd:
            context["err_text"] = "两次密码输入不一致"
            return render(request, "register.html", context)

        if not allow:
            context["err_text"] = "请勾选用户协议"
            return render(request, "register.html", context)

        if UserInfo.objects.filter(username=uname).count() >= 1:
            context["err_text"] = "用户名已注册"
            return render(request, "register.html", context)

        if UserInfo.objects.filter(email=email).count() >= 1:
            context["err_text"] = "邮箱已注册"
            return render(request, "register.html", context)

        # 执行注册操作
        try:
            user = UserInfo.objects.create_user(uname, email, upwd)
        except Exception:
            context["err_text"] = "用户信息录入失败，请重新输入"
            return render(request, 'register.html', context)
        user.is_active = False
        print('user',user)
        print('usertype',type(user))
        user.save()
        print(user.toJSON())
        send_user_active.delay(user.id,user.email)

        return HttpResponse("请在两个小时内，接收邮件进行激活。")


def exists(request):
    uname = request.GET.get("uname")
    result=0
    if uname is not None:
        result = UserInfo.objects.filter(username=uname).count()
    uemail = request.GET.get("email")

    if uemail is not None:
        result = UserInfo.objects.filter(email=uemail).count()

    return JsonResponse({"result": result})


def active(request, value):
    serializer = Serializer(settings.SECRET_KEY)
    try:
        dict = serializer.loads(value)
        user = UserInfo.objects.get(pk=dict['id'])
        user.is_active = True
        user.save()
        return HttpResponse("用户激活成功，跳转登陆页进行登陆：<a href='/user/login'>登陆login</a>")
    except SignatureExpired as e:
        return HttpResponse("已过期")

class LoginView(View):
    def get(self,request):
        uname = request.COOKIES.get("uname",'')
        context = {
            "title": "登陆",
            "username":uname,
            "err_info":""
        }
        return render(request,"login.html",context)
    def post(self,request):
        # 接收数据
        dict=request.POST
        uname = dict.get("username")
        upwd = dict.get("pwd")
        remember = dict.get("remember")

        context = {
            "title": "登陆",
            "username":uname,
            "pwd": upwd,
            "err_info":""
        }

        # 验证数据
        if not all([uname,upwd]):
            context["err_info"]="请填写完整信息"
            return render(request,"login.html",context)
        #用户信息验证并跳转
        user = authenticate(username=uname,password=upwd)

        if not user:
            context["err_info"] = "用户名或密码错误"
            return render(request, "login.html", context)

        if not user.is_active:
            context["err_info"] = "邮箱未激活，请登陆邮箱进行激活"
            return render(request, "login.html", context)

        login(request,user)

        # 设置记录用户名
        response = redirect("/user/info")
        if remember is not None:
            response.set_cookie("uname", uname, expires=60 * 60 * 24 * 30)
        else:
            response.delete_cookie("uname")
        return response # HttpResponse("登陆成功")# redirect("/user/info")



