from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone


from .models import Category, Comment, Post, User
from .forms import CommentForm, EditProfileForm, PostForm


def get_published_posts(posts=Post.objects, filter_published=False,
                        select_related_fields=None, annotate_comments=False):
    queryset = posts

    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    if select_related_fields:
        queryset = queryset.select_related(*select_related_fields)

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.order_by(*Post._meta.ordering)


def get_paginated_response(queryset, request, per_page=10):
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'blog/index.html', {
        'page_obj': get_paginated_response(
            get_published_posts(filter_published=True, annotate_comments=True),
            request)
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(get_published_posts(filter_published=True),
                                 pk=post_id)

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all()
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': get_paginated_response(
            get_published_posts(posts=category.posts, filter_published=True),
            request)
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:profile', request.user.username)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = get_object_or_404(Post, id=post_id)
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/comment.html', {'form': form,
                                                 'comment': comment,
                                                 'post': comment.post})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=comment.post.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=comment.post.id)

    return render(request, 'blog/comment.html', {'comment': comment,
                                                 'post': comment.post})


def user_profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = get_published_posts(
        posts=author.posts,
        filter_published=request.user != author,
        annotate_comments=True)

    return render(request, 'blog/profile.html', {
        'profile': author,
        'page_obj': get_paginated_response(posts, request)
    })


@login_required
def edit_profile(request):
    user = request.user
    form = EditProfileForm(request.POST or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', user.username)

    return render(request, 'blog/user.html', {'form': form})
