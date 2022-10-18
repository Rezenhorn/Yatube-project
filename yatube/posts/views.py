from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def paginator(page_number, posts):
    """Вспомогательная функция для паджинатора."""
    paginator = Paginator(posts, settings.POSTS_NUM)
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Главная страница."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator(request.GET.get('page'), posts),
        'title': 'Последние обновления на сайте',
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница постов группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': paginator(request.GET.get('page'), posts),
        'title': f'Записи сообщества {group.title}',
    }
    return render(request, template, context)


def profile(request, username):
    """Страница пользователя."""
    template = 'posts/profile.html'
    author = get_object_or_404(
        User.objects.select_related('profile'), username=username)
    posts = author.posts.select_related('group')
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    context = {
        'author': author,
        'page_obj': paginator(request.GET.get('page'), posts),
        'following': following,
        'title': f'Профайл пользователя {author}',
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Создание комментария к посту."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def edit_comment(request, comment_id):
    """Редактирование коммента."""
    template = 'posts/edit_comment.html'
    comment = get_object_or_404(
        Comment.objects.select_related('author'), pk=comment_id
    )
    if request.user.pk != comment.author.pk:
        return redirect('posts:post_detail', comment.post.pk)
    form = CommentForm(
        instance=comment,
        data=request.POST or None,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', comment.post.pk)
    context = {
        'form': form,
        'title': 'Редактировать коммент'
    }
    return render(request, template, context)


@login_required
def del_comment(request, comment_id):
    """Удаление коммента."""
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user.pk != comment.author.pk:
        return redirect('posts:post_detail', comment.post.pk)
    comment.delete()
    return redirect('posts:post_detail', comment.post.pk)


def post_detail(request, post_id):
    """Информация о посте."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related(
            Prefetch('comments', Comment.objects.select_related('author'))
        ),
        pk=post_id
    )
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Создание поста."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, {'form': form, 'title': 'Новый пост'})


@login_required
def post_edit(request, post_id):
    """Редактирование поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    if request.user.pk != post.author.pk:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        instance=post,
        data=request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'form': form,
        'is_edit': True,
        'title': 'Редактировать пост'
    }
    return render(request, template, context)


@login_required
def post_del(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user.pk != post.author.pk:
        return redirect('posts:index')
    post.delete()
    return redirect('posts:index')


@login_required
def follow_index(request):
    """Подписки пользователя."""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator(request.GET.get('page'), posts),
        'title': 'Ваши подписки',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author).delete()
    return redirect('posts:follow_index')
