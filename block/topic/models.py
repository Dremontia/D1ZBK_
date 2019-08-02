from django.db import models

# Create your models here.
from user.models import UserProject


class Topic(models.Model):
    title = models.CharField(verbose_name='文章主题', max_length=50)
    # tec技术类 no-tec非技术类
    category = models.CharField(verbose_name='博客分类', max_length=20)
    # public公开 private私有
    limit = models.CharField(verbose_name='权限', max_length=10)
    introduce = models.CharField(verbose_name='简介', max_length=90)
    content = models.TextField(verbose_name='内容')
    # auto_now_add创建时自动添加当前时间
    created_time = models.DateTimeField(auto_now_add=True)
    # auto_now 为true 每次修改都会变更为修改的当前时间
    modified_time = models.DateTimeField(auto_now=True)
    # 外键
    author = models.ForeignKey(UserProject)

    class Meta:
        db_table = 'topic'
