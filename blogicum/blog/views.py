from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone


from .models import Category, Comment, Post, User
from .forms import CommentForm, EditProfileForm, PostForm


def get_published_posts(queryset=Post.objects, is_published=True,
                        pub_date_check=True, category_published=True):
    qs = queryset
    if is_published:
        qs = qs.filter(is_published=True)
    if pub_date_check:
        qs = qs.filter(pub_date__lte=timezone.now())
    if category_published:
        qs = qs.filter(category__is_published=True)
    return qs


def get_paginated_response(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    posts = get_published_posts().select_related('author').prefetch_related(
        'category').annotate(comment_count=Count('comments')).order_by(
        '-pub_date')
    return render(request, 'blog/index.html', {
        'page_obj': get_paginated_response(posts, request)})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(get_published_posts(), pk=post_id)

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all()
    })


def category_posts(request, category_slug):
    category_object = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = category_object.posts.filter(is_published=True,
                                         pub_date__lte=timezone.now())
    return render(request, 'blog/category.html', {
        'category': category_object,
        'page_obj': get_paginated_response(posts, request)
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)

    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)

    return render(request, 'blog/comment.html',
                  {'form': form, 'comment': comment, 'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)

    return render(request, 'blog/comment.html', {'comment': comment,
                                                 'post': post})


def user_profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date')
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
        return redirect('blog:profile', username=user.username)

    return render(request, 'blog/user.html', {'form': form})
