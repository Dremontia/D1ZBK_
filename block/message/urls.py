from django.conf.urls import url, include

from message import views

urlpatterns = [
    url(r'^/(?P<topic_id>[\d]+)$', views.messages, name='messages')

]
