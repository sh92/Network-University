from django.conf.urls import url
from .views import (
    phue_transfer,
    on_off,
    change123,
    changeColor,
    changeBright,
	)

urlpatterns = [
	url(r'^$', phue_transfer),
    url(r'^on_off/$', on_off),
    url(r'^change123/$', change123),
    url(r'^changeColor/$', changeColor),
    url(r'^changeBright/$', changeBright),
]
