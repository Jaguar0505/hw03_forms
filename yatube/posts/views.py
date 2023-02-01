from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    posts = Post.objects.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    posts = Post.objects.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)[:10]

    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def group_list(request, slug):
    posts = Post.objects.all()

    group = get_object_or_404(Group, slug=slug)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'posts/group_list.html'

    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'page_obj': page_obj,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id)

    author_posts = post.author.posts.all()

    context = {
        'post': post,
        'author_posts': author_posts,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/update_post.html', context)


class JustStaticPage(TemplateView):
    template_name = 'app_name/just_page.html'


class AboutAuthorView(TemplateView):
    template_name = 'app_name/author.html'


class AboutTechView(TemplateView):
    template_name = 'app_name/tech.html'
