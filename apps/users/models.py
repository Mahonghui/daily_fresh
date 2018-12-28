from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from db.base_model import BaseModel

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    '''用户信息表'''

    username = models.CharField(max_length=20, verbose_name='用户名', unique=True)
    first_name = models.CharField(max_length=10, verbose_name='名')
    last_name = models.CharField(max_length=10, verbose_name='姓')
    email = models.EmailField(max_length=255, verbose_name='邮箱')

    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_superuser = models.BooleanField(default=False, verbose_name='是否是管理员')
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def generate_active_token(self):
        '''生成用户签名'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': self.id}
        token = serializer.dumps(info)
        return token.decode()

    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class AddressManager(models.Manager):

    def get_default_address(self, user):
        try:
            address = self.get(user=user, is_default=True)
        except self.model.DoesNotExist:
            address = None
        return address

class Address(BaseModel):
    '''地址表'''

    receiver = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, verbose_name='邮编')
    contact = models.CharField(max_length=11, verbose_name='联系方式')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    # 定义外键
    user = models.ForeignKey('User', verbose_name='所属用户', on_delete=models.CASCADE)
    objects = AddressManager()

    class Meta:
        db_table = 'Address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
