
from django.urls import path
from . import views

app_name = 'catalog'
urlpatterns = [
    # Страница со списком архитектурных объектов
    path('', views.catalog_list, name='catalog_list'),

    # Подробная страница отдельного архитектурного объекта
    path('<slug:slug>/', views.object_detail, name='object_detail'),
]
