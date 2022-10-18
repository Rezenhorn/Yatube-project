from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import CreationForm
from .models import Profile


class SignUp(CreateView):
    """Регистрация пользователя."""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""
    model = Profile
    fields = ('bio', 'profile_pic')
    success_url = reverse_lazy('posts:index')

    def get_object(self):
        return self.request.user.profile
