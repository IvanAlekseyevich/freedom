<<<<<<< HEAD
<<<<<<< HEAD
from django.http import HttpResponse
# Импортируем модель, чтобы обратиться к ней
from .models import Post
=======
=======
>>>>>>> parent of 5487f2c (Added admin and post (test))
from django.shortcuts import render

>>>>>>> parent of 5487f2c (Added admin and post (test))

def index(request):
    template = 'posts/index.html'
    text = 'Это главная страница проекта Yatube'
    context = {
        'text': text,
    }
    return render(request, template, context) 


# В урл мы ждем парметр, и нужно его прередать в функцию для использования
def group_posts(request, slug):
    template = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'text': text,
    }
<<<<<<< HEAD
<<<<<<< HEAD
    return render(request, 'posts/group_list.html', context) 

=======
=======
>>>>>>> parent of 5487f2c (Added admin and post (test))
    return render(request, template, context) 

def group_list(request):
    template = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'text': text,
    }
<<<<<<< HEAD
    return render(request, template, context) 
>>>>>>> parent of 5487f2c (Added admin and post (test))
=======
    return render(request, template, context) 
>>>>>>> parent of 5487f2c (Added admin and post (test))
