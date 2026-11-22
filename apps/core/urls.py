
from django.urls import path
from . import views

urlpatterns = [
    # Главная страница базы знаний
    path('', views.home, name='home'),
]
