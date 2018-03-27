from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.views.generic import View
import re
from .models import UserInfo, AddrInfo, AreaInfo
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_user_active
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from utils.views import LoginRequiredViewMixin
from django_redis import get_redis_connection
from tt_goods.models import GoodsSKU

# Create your views here.
class RegisterView(View):
    def get(self, request):
        """处理get请求，返回注册页面"""
        return render(request, "register.html", {"title": "注册"})

    def post(self, request):
        """处理post请求，进行注册验证"""
        dict = request.POST
        uname = dict.get("user_name")
        upwd = dict.get("pwd")
        cpwd = dict.get("cpwd")
        email = dict.get("email")
        allow = dict.get("allow")
        err_text = ""

        context = {'uname': uname, 'upwd': upwd, 'cpwd': cpwd, 'email': email, 'err_text': err_text, "title": "注册"}

        # # 注册信息校验
        # if not all([uname, upwd, cpwd, email]):
        #     context["err_text"] = "请输入完整信息"
        #     return render(request, "register.html", context)
        #
        # if len(uname) < 5 | len(uname) > 20:
        #     context["err_text"] = "用户名格式不正确，请重新输入"
        #     return render(request, "register.html", context)
        #
        # if len(upwd) < 8 | len(upwd) > 20:
        #     context["err_text"] = "密码格式不正确，请重新输入"
        #     return render(request, "register.html", context)
        #
        # if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #     context["err_text"] = "邮箱格式不正确，请重新输入"
        #     return render(request, "register.html", context)
        #
        # if not cpwd == upwd:
        #     context["err_text"] = "两次密码输入不一致"
        #     return render(request, "register.html", context)
        #
        # if not allow:
        #     context["err_text"] = "请勾选用户协议"
        #     return render(request, "register.html", context)
        #
        # if UserInfo.objects.filter(username=uname).count() >= 1:
        #     context["err_text"] = "用户名已注册"
        #     return render(request, "register.html", context)
        #
        # if UserInfo.objects.filter(email=email).count() >= 1:
        #     context["err_text"] = "邮箱已注册"
        #     return render(request, "register.html", context)

        # 执行注册操作
        try:
            user = UserInfo.objects.create_user(uname, email, upwd)
        except Exception:
            context["err_text"] = "用户信息录入失败，请重新输入"
            return render(request, 'register.html', context)
        user.is_active = False
        print('user', user)
        print('usertype', type(user))
        user.save()
        print(user.toJSON())
        send_user_active.delay(user.id, user.email)

        return HttpResponse("请在两个小时内，接收邮件进行激活。")


def exists(request):
    uname = request.GET.get("uname")
    result = 0
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
    def get(self, request):
        uname = request.COOKIES.get("uname", '')
        context = {
            "title": "登陆",
            "username": uname,
            "err_info": ""
        }
        return render(request, "login.html", context)

    def post(self, request):
        # 接收数据
        dict = request.POST
        uname = dict.get("username")
        upwd = dict.get("pwd")
        remember = dict.get("remember")

        context = {
            "title": "登陆",
            "username": uname,
            "pwd": upwd,
            "err_info": ""
        }

        # 验证数据
        if not all([uname, upwd]):
            context["err_info"] = "请填写完整信息"
            return render(request, "login.html", context)
        # 用户信息验证并跳转
        user = authenticate(request, username=uname, password=upwd)
        print(user)

        if user is None:
            context["err_info"] = "用户名或密码错误"
            return render(request, "login.html", context)

        if not user.is_active:
            context["err_info"] = "邮箱未激活，请登陆邮箱进行激活"
            return render(request, "login.html", context)

        login(request, user)

        # 登陆成功，根据next参数决定跳转方向
        next = request.GET.get('next', "/")  # 设置跳转路径，默认返回登录页面
        response = redirect(next)

        # 设置记录用户名
        if remember is not None:
            response.set_cookie("uname", uname, expires=60 * 60 * 24 * 30)
        else:
            response.delete_cookie("uname")
        return response  # HttpResponse("登陆成功")# redirect("/user/info")


def userlogout(request):
    logout(request)
    return redirect("/user/login")


@login_required
def info(request):

    client = get_redis_connection()
    history_list=client.lrange("history%d"%request.user.id,0,-1)
    history_list2=[]
    if history_list:
        for gid in history_list:
            history_list2.append(GoodsSKU.objects.get(id=gid))

    user_info = request.user.addrinfo_set.all().filter(isDefault=True)
    if user_info:
        user_info=user_info[0]
    else:
        user_info=""

    context = {
        "title": "用户页面",
        "user_info":user_info,
        "history_list":history_list2
    }
    return render(request, "user_center_info.html", context)


@login_required
def order(request):
    context = {
        "title": "用户订单",
    }
    return render(request, "user_center_order.html", context)


class SiteView(LoginRequiredViewMixin, View):
    def get(self, request):
        addr_list = AddrInfo.objects.filter(user=request.user)
        print(addr_list)

        context = {
            "title": "收货地址",
            "addr_list": addr_list,
        }
        return render(request, "user_center_site.html", context)

    def post(self, request):
        addr_list = AddrInfo.objects.filter(user=request.user)
        dict = request.POST
        receiver = dict.get("receiver")
        province = dict.get("province")
        city = dict.get("city")
        district = dict.get("district")
        addr = dict.get("addr")
        code = dict.get("code")
        phone_numbe = dict.get("phone")
        isDefault = dict.get("isDefault")
        if not isDefault:
            isDefault = False

        context = {
            "title": "收货地址",
            'receiver': receiver,
            'province': province,
            'city': city,
            'district': district,
            'addr': addr,
            'code': code,
            'phone_numbe': phone_numbe,
            'isDefault': isDefault,
            'err_info': "",
            "addr_list": addr_list,
        }

        if not all([receiver, province, city, district, addr, code, phone_numbe]):
            context["err_info"] = "您的信息填写不完整"
            return render(request, 'user_center_site.html', context)


        # 验证信息
        if len(receiver)>10:
            context["err_info"] = "收件名过长"
            return render(request, 'user_center_site.html', context)
        if len(code)>6:
            context["err_info"] = "邮政编码过长"
            return render(request, 'user_center_site.html', context)
        if province=='”0”':
            context["err_info"] = "请选择省份"
            return render(request, 'user_center_site.html', context)
        if city=='”0”':
            context["err_info"] = "请选择城市"
            return render(request, 'user_center_site.html', context)
        if not len(phone_numbe)==11:
            context["err_info"] = "请正确填写11位手机号码"
            return render(request, 'user_center_site.html', context)



        # 存储地址信息
        # addr_sit = AddrInfo.objects.create(**{
        #     "receiver": receiver,
        #     "province_id": province,
        #     "city_id": city,
        #     "district_id": district,
        #     "addr": addr,
        #     "code": code,
        #     "phone_number": phone_numbe,
        #     "isDefault": isDefault,
        #     "user": request.user,
        # })
        addr_sit = AddrInfo()
        addr_sit.receiver=receiver
        addr_sit.province_id=province
        addr_sit.city_id=city
        addr_sit.district_id=district
        addr_sit.addr=addr
        addr_sit.code=code
        addr_sit.phone_number=phone_numbe
        if isDefault is not False:
            addr_sit.isDefault=True
        else:
            addr_sit.isDefault = False
        addr_sit.user=request.user

        print(context)
        addr_sit.save()
        return HttpResponseRedirect("/user/addr")
        # return redirect("/user/addr")


def addarea(request):
    pid = request.GET.get("id")
    if pid==None:
        site_list = AreaInfo.objects.filter(aParent=None)
    else:
        site_list = AreaInfo.objects.filter(aParent=pid)

    result = []

    for site in site_list:
        result.append({
            "id": site.id,
            "title": site.title,
        })
    context = {"result": result}
    return JsonResponse(context)
