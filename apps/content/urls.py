from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.content_home, name='content_home'),
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('images/', views.images_list, name='images_list'),
    path('videos/', views.videos_list, name='videos_list'),
]