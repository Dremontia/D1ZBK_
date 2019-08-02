from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.topic, name='topic'),
    # http://127.0.0.1:8000/v1/topics/<author_id>
    url(r'/(?P<author_id>[\w]+)$', views.topics, name='topics'),
    url(r'/(?P<username>[\w]+)', views.topics, name='topics'),
]
