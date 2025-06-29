from django.conf import settings
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView
from django.conf.urls.static import static

from users.forms import CustomUserCreationForm
from users.views import user_profile, edit_profile


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('profile/<str:username>/', user_profile, name='user_profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
