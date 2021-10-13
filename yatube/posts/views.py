from django.shortcuts import render, get_object_or_404

from .models import Post, Group


def index(request):
    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context) 


def group_posts(request, slug):
    # Функция get_object_or_404 получает по заданным критериям объект 
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context) 

#def index(request):
#    template = 'posts/index.html'
#    text = 'Это главная страница проекта Yatube'
#    context = {
#        'text': text,
#    }
#    return render(request, template, context) 

# def group_list(request):
#     template = 'posts/group_list.html'
#     text = 'Здесь будет информация о группах проекта Yatube'
#     context = {
#         'text': text,
#     }
#     return render(request, template, context) 

# В урл мы ждем парметр, и нужно его прередать в функцию для использования
# def group_posts(request, slug):
#     template = 'posts/group_list.html'
#     text = 'Здесь будет информация о группах проекта Yatube'
#     context = {
#         'text': text,
#     }
#     return render(request, template, context) 

# View-функция для страницы сообщества: