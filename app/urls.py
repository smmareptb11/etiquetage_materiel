# -*- coding: utf-8 -*-

from .views import MatDetailJson
from django.urls import path

app_name = "app"

urlpatterns = [path(
	"mat/detail-json/<int:vMatId>/",
	MatDetailJson.as_view(),
	name="matDetailJson"
)]