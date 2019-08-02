from django.db import models


# Create your models here.
class UserProject(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=11, primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=30)
    email = models.EmailField(verbose_name='邮箱')
    password = models.CharField(verbose_name='密码', max_length=64)
    sign = models.CharField(verbose_name='个性签名', max_length=50, null=True)
    info = models.CharField(verbose_name='个人描述', max_length=150, null=True)
    avatar = models.ImageField(upload_to='avatar/', verbose_name='头像字段', null=True)

    class Meta:
        db_table = 'user_profile'
