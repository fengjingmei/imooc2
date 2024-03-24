from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout #authenticate 判断是否存在
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import redis
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, UploadImageForm
from apps.users.forms import UserInfoForm, ChangePwdForm
from apps.users.forms import RegisterGetForm, RegisterPostForm, UpdateMobileForm
from apps.utils.YunPian import send_single_sms
from apps.utils.random_str import generate_random
from imooc.settings import yp_apikey, REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile
from apps.operations.models import UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Course


class CustomAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def message_nums(request):
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()}
    else:
        return {}


class MyMessageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        messages = UserMessage.objects.filter(user=request.user)
        current_page = "message"
        for message in messages:
            message.has_read = True
            message.save()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(messages, per_page=3, request=request)
        messages = p.page(page)

        return render(request, "usercenter-message.html",{
            "messages":messages,
            "current_page":current_page
        })


class MyFavCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_course"
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            try:
                course = Course.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Course.DoesNotExist as e:
                pass
        return render(request, "usercenter-fav-course.html",{
            "course_list":course_list,
            "current_page":current_page
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_teacher"
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            org = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(org)
        return render(request, "usercenter-fav-teacher.html",{
            "teacher_list":teacher_list,
            "current_page":current_page
        })


class MyFavOrgView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfavorg"
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html",{
            "org_list":org_list,
            "current_page":current_page
        })


class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mycourse"
        # my_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html",{
            # "my_courses":my_courses,
            "current_page":current_page
        })


class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        mobile_form = UpdateMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({
                    "mobile":"该手机号码已经被占用"
                })
            user = request.user
            user.mobile = mobile
            user.username = mobile
            user.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(mobile_form.errors)



#用户个人中心——修改密码
class ChangePwdView(LoginRequiredMixin, View):
    login_url = "/login/"
    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            user = request.user
            user.set_password(pwd1)
            user.save()

            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(pwd_form.errors)


#上传用户头像
class UploadImageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        #处理用户上传的头像
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse({
                "status": "fail"
            })


#进入个人中心页面
class UserInfoView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        return render(request, "usercenter-info.html",{
            "captcha_form":captcha_form,
            "current_page":current_page
        })

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status":"success"
            })
        else:
            return JsonResponse(user_info_form.errors)


#用户注册
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        return render(request, "register.html", {
            "register_get_form":register_get_form
        })

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        if register_post_form.is_valid():
            mobile = register_post_form.cleaned_data["mobile"]
            password = register_post_form.cleaned_data["password"]
            # 新建一个用户
            user = UserProfile(username=mobile)
            user.set_password(password)
            user.mobile = mobile
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            register_get_form = RegisterGetForm()
            return render(request, "register.html", {
                "register_get_form":register_get_form,
                "register_post_form": register_post_form
            })


#动态登录
class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        banners = Banner.objects.all()[:3]
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
            "banners":banners
        })

    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():
            #没有注册账号依然可以登录
            mobile = login_form.cleaned_data["mobile"]
            existed_users = UserProfile.objects.filter(mobile=mobile) #filter不抛异常，get抛
            if existed_users:
                user = existed_users[0]
                #login(request,user)
            else:
                #新建一个用户
                user = UserProfile(username=mobile)
                password = generate_random(10, 2) #明文
                user.set_password(password)  #加密
                user.mobile = mobile
                user.save()
            login(request, user)
            next = request.GET.get("next", "")
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse("index"))
        else:
            d_form = DynamicLoginForm()
            return render(request, "login.html", {"login_form": login_form,
                                                  "d_form": d_form,
                                                  "banners":banners,
                                                  "dynamic_login":dynamic_login})


#动态登录时发送验证码
class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)
        re_dict = {}
        if send_sms_form.is_valid():
            mobile = send_sms_form.cleaned_data["mobile"]
            #随机生成数字验证码
            code = generate_random(4, 0)
            re_json = send_single_sms(yp_apikey,code,mobile=mobile)  #发送验证码
            if re_json["code"] == 0:  #验证成功
                re_dict["status"] = "success"
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
                r.set(str(mobile), code)
                r.expire(str(mobile), 60*5) #设置验证码五分钟过期
            else:
                re_dict["msg"] = re_json["msg"]
        else:
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)


#用户退出登录
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


#用户登录
class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:  #进入登陆页面，如果用户已经登陆，则跳转到首页
            return HttpResponseRedirect(reverse("index"))

        banners = Banner.objects.all()[:3]
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html",{
            "login_form":login_form,
            "next":next,
            "banners":banners
        })

    def post(self, request, *args, **kwargs):
        #表单验证 获取用户名与密码
        login_form = LoginForm(request.POST) #实例化
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():
            #用于通过用户和密码查询用户是否存在
            user_name = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]

            #用于通过用户名和密码查询用户是否存在
            user = authenticate(username=user_name, password=password)
            if user is not None:
                #查询到用户
                login(request, user)
                #登录成功之后应该怎么跳转到首页
                next = request.GET.get("next", "")
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse("index")) #重定向回首页
            else:
                #未查询到用户
                return render(request, "login.html", {"msg":"用户名或密码错误", "login_form": login_form, "banners":banners})
        else:
            return render(request, "login.html", {"login_form": login_form,
                                                  "banners":banners})


