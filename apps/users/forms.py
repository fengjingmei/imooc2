from django import forms
from captcha.fields import CaptchaField
#import redis

#from imooc.settings import REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile


class UpdateMobileForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data


class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

    def clean(self):
        pwd1 = self.cleaned_data["password1"]
        pwd2 = self.cleaned_data["password2"]

        if pwd1 != pwd2:
            raise forms.ValidationError("密码不一致")
        return self.cleaned_data


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name", "gender", "birthday", "address"]


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]


class RegisterGetForm(forms.Form): #获得图片验证码
    captcha = CaptchaField()


class RegisterPostForm(forms.Form):  #注册登录时的上传表单
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)
    password = forms.CharField(required=True)

    def clean_mobile(self):
        mobile = self.data.get("mobile")
        # 验证手机号码是否已经注册
        users = UserProfile.objects.filter(mobile=mobile)
        if users:
            raise forms.ValidationError("该手机号码已注册")
        return mobile

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return code


class LoginForm(forms.Form):  ##登陆表单
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)


class DynamicLoginForm(forms.Form):  #动态登陆的图片验证码
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    captcha = CaptchaField()


class DynamicLoginPostForm(forms.Form): #动态登陆时提交的表格信息
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4) #手机验证码

    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data


