from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from .forms import PostForm, CommentForm
from .models import Post, Group, User


def index(request):
    post_list = Post.objects.all()
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
    count = post_list.count()
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
    count = post_detail.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post_detail.comments.all()
    context = {
        'count': count,
        'post_detail': post_detail,
        'form': form,
        'comments': comments
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    # Если пришёл не POST-запрос - создаём и передаём в шаблон пустую форму
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form})
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    # Если условие if form.is_valid() ложно и данные не прошли валидацию - 
    # передадим полученный объект в шаблон,
    # чтобы показать пользователю информацию об ошибке
    # Заодно заполним все поля формы данными, прошедшими валидацию, 
    # чтобы не заставлять пользователя вносить их повторно
    return render(request, template, {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
    else:
        form = PostForm(instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': 'is_edit',
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
