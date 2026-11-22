
from django.urls import path
from . import views

app_name = 'references'

urlpatterns = [
    # Главная страница справочников
    path('', views.references_home, name='references_home'),

    # Список городов
    path('cities/', views.cities_list, name='cities_list'),

    # Список архитектурных стилей
    path('styles/', views.styles_list, name='styles_list'),

    # Список исторических эпох
    path('epochs/', views.epochs_list, name='epochs_list'),

    # Список архитекторов
    path('architects/', views.architects_list, name='architects_list'),
]
