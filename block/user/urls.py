from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.users, name='user'),
    # http://127.0.0.1:8000/v1/users/<username>
    url(r'^/(?P<username>[\w]+)$', views.users),
    # http://127.0.0.1:8000/v1/users/<username>/avatar
    url(r'^/(?P<username>[\w]+)/avatar$', views.avatar),
]
