from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm


def get_published_posts():
    return Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def get_paginated_response(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = get_published_posts().order_by('-pub_date')
    page_obj = get_paginated_response(posts, request)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, pk):
    if request.user.is_authenticated:

        post = get_object_or_404(Post, pk=pk)
    else:
        post = get_object_or_404(get_published_posts(), pk=pk)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category_object = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_published_posts().filter(category=category_object)
    page_obj = get_paginated_response(posts, request)
    return render(request, 'blog/category.html', {
        'category': category_object,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('user_profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('blog:post_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


# @login_required
# def add_comment(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             return redirect('blog:post_detail', pk=post.pk)
#     else:
#         form = CommentForm()
#     return render(request, 'blog/comment.html', {'form': form,
#                                                  'post': post})


# @login_required
# def edit_comment(request, post_id, comment_id):
#     comment = get_object_or_404(Comment, id=comment_id)
#     post = comment.post
#     if comment.author != request.user:
#         return redirect('blog:post_detail', pk=post.id)

#     if request.method == 'POST':
#         form = CommentForm(request.POST, instance=comment)
#         if form.is_valid():
#             form.save()
#             return redirect('blog:post_detail', pk=post_id)
#     else:
#         form = CommentForm(instance=comment)

#     return render(request, 'blog/comment.html', {'form': form})
