from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10) 
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context) 

def group_posts(request, slug): 
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    template = 'posts/group_list.html'
    return render(request, template, context) 

def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    count= post_list.count()
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': user,
        'count': count,
        'page_obj': page_obj,
    }
    template = 'posts/profile.html'
    return render(request, template, context)

def post_detail(request, post_id):
    post_detail = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author=post_detail.author).count()
    context = {
        'count': count,
        'post_detail': post_detail,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)

@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse('posts:profile', args=(request.user,)))

        # Если условие if form.is_valid() ложно и данные не прошли валидацию - 
        # передадим полученный объект в шаблон,
        # чтобы показать пользователю информацию об ошибке
        # Заодно заполним все поля формы данными, прошедшими валидацию, 
        # чтобы не заставлять пользователя вносить их повторно
        return render(request, template, {'form': form})

    # Если пришёл не POST-запрос - создаём и передаём в шаблон пустую форму
    # пусть пользователь напишет что-нибудь
    form = PostForm()
    return render(request, template, {'form': form}) 

def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'GET' and request.user != post.author:
        return HttpResponseRedirect(reverse('posts:post_detail', args=(post_id,)))
    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if request.user != post.author:
            return HttpResponseRedirect(reverse('posts:post_detail', args=(post_id,)))
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('posts:post_detail', args=(post_id,)))
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': 'is_edit',
    }
    template = 'posts/create_post.html'
    return render(request, template, context)
