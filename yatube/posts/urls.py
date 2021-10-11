# posts/urls.py
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='main_page'),
    path('group_list', views.group_posts, name='group_page'),
] 