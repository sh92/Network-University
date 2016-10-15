from django.conf.urls import url
from .views import (
    smtp_transfer,
    complete_method,
	)

urlpatterns = [
	url(r'^$', smtp_transfer),
    url(r'^complete/$', complete_method),
]
