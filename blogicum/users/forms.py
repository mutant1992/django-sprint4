from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',
                                                 'first_name',
                                                 'last_name')


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Логин"
        self.fields['first_name'].label = "Имя"
        self.fields['last_name'].label = "Фамилия"
        self.fields['email'].label = "Электронная почта"
