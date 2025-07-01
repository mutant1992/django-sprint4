from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from users.forms import EditProfileForm
from blog.models import Post
from blog.views import get_paginated_response

myuser = get_user_model()


def user_profile(request, username):
    profile = get_object_or_404(myuser, username=username)
    posts = Post.objects.filter(author=profile)
    page_obj = get_paginated_response(posts, request)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    user = get_object_or_404(myuser, username=username)

    if request.user != user:
        raise PermissionDenied("Нет прав для редактирования этого профиля")
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=user.username)
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'blog/user.html', {'form': form})
