import os
import json
from urllib.request import urlopen
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, DetailView
from .models import CardUser
from .forms import UserForm


def login_view(request):
    context = {'title': 'Login'}
    if request.method == 'POST':
        username = request.POST['username']
        pw = request.POST['password']
        user = authenticate(request, username=username, password=pw)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, 'Login Failed')
            context['form'] = AuthenticationForm()
    else:
        context['form'] = AuthenticationForm()
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'logout successful')
    return HttpResponseRedirect('/users/')


class UserDetail(LoginRequiredMixin, DetailView):
    model = CardUser
    template_name = 'users/user_detail.html'


class UserUpdate(LoginRequiredMixin, UpdateView):
    model = CardUser
    template_name = 'users/user_update.html'
    form_class = UserForm

    def form_valid(self, form):
        user = form.save(commit=True)
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        return redirect('users:user-profile', self.kwargs.get('pk'))


def weather(request):
    api_uri = os.environ.get('WX_API')
    with urlopen(api_uri) as response:
        source = response.read()

    data = json.loads(source)

    print(json.dumps(data, indent=2))

    loc = data['location']['name']
    st = data['location']['region']
    temp = data['current']['temp_c']
    temp_f = data['current']['temp_f']
    cond = data['current']['condition']['text']
    wind = data['current']['wind_mph']
    wind_g = data['current']['gust_mph']

    report = f'It is currently {temp}C ({temp_f}F) ' \
             f'and {cond} with winds of {wind} mph (gusts up to {wind_g} mph) in {loc}, {st}'

    return render(request, 'users/weather.html', {'title': 'Weather Information', 'report': report})
