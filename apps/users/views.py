from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistrationForm

class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
