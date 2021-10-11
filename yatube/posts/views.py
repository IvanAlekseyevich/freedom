from django.shortcuts import render


def index(request):
    template = 'posts/index.html'
    text = 'Последние обновления на сайте'
    context = {
        'text': text,
    }
    return render(request, template, context) 


# В урл мы ждем парметр, и нужно его прередать в функцию для использования
def group_posts(request):
    template = 'posts/group_list.html'
    text = 'Лев Толстой – зеркало русской революции.'
    context = {
        'text': text,
    }
    return render(request, template, context) 