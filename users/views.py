import os
import json
from urllib.request import urlopen
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import UpdateView, DetailView
from .models import CardUser
from .forms import UserForm, LoginForm


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
            context['form'] = LoginForm()
    else:
        context['form'] = LoginForm()
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


def toggle_view_mode(request, mode: str = None):
    if mode is not None:
        if mode == 'dark':
            response = HttpResponse('<i class="fa fa-sun-o"></i>')
            response.set_cookie('toggle_mode', 'dark')
        else:
            response = HttpResponse('<i class="fa fa-moon-o"></i>')
            response.set_cookie('toggle_mode', None)
    else:
        response = HttpResponse('<i class="fa fa-moon-o"></i>')
        response.set_cookie('toggle_mode', None)
    return response
