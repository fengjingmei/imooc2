from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

GENDER_CHOICES = (
    ("male", "男"),
    ("female", "女")
)


class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(verbose_name="性别", choices=GENDER_CHOICES, max_length=6)
    address = models.CharField(max_length=100, verbose_name="地址", default="")
    mobile = models.CharField(max_length=11, verbose_name="手机号码")
    image = models.ImageField(verbose_name="用户头像", upload_to="head_image/%Y/%m", default="default.jpg")
    #upload_to="head_image/%Y/%m" 上传头像，自动创建head_image文件夹，之后按照年，月创建文件夹
    #default="default.jpg" 默认头像

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def unread_nums(self):
        #未读消息数量
        return self.usermessage_set.filter(has_read=False).count()

    def __str__(self):
        if self.nick_name:
            return self.nick_name
        else:
            return self.username


class BaseModel(models.Model):
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")  #利于日志分析

    class Meta:
        abstract = True   #不会生成表