
"""Маршруты глобального поиска."""

from django.urls import path

from apps.search import views


urlpatterns = [
    path('', views.global_search, name='global_search'),
]
