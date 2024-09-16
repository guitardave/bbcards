from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import UpdateView, DetailView
from .models import CardUser
from .forms import UserForm, LoginForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            pw = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=pw)
            if user is not None:
                login(request, user)
                return redirect('cards:card-list-50')
            else:
                messages.warning(request, 'Login Failed')
        else:
            messages.warning(request, 'Login error')
    return render(request, 'users/login.html', {'title': 'Login', 'form': LoginForm})


def logout_view(request):
    logout(request)
    messages.info(request, 'logout successful')
    return redirect('users:login')


@login_required(login_url='/users/')
def user_management_list(request):
    if not request.user.is_superuser:
        messages.warning(request, 'Unauthorized Access')
        return redirect('users:user-profile', request.user.id)
    if request.method == 'POST':
        form = UserForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'User saved successfully')
            return redirect('users:user-management')
    form = UserForm
    context = {
        'title': 'User Management',
        'form': form,
        'users': CardUser.objects.filter(is_active=True),
        'c_title': 'Add User'
    }
    return render(request, 'users/user_management.html', context)


@login_required(login_url='/users/')
def user_management_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            message = 'User added successfully'
            context = {
                'users': CardUser.objects.filter(is_active=True).order_by('first_name'),
                'message': message
            }
            return render(request, 'users/user_management_table_partial.html', context)
    context = {'form': UserForm}
    return render(request, 'users/user_management_form_partial.html', context)


@login_required(login_url='/users/')
def user_management_update(request, pk: int):
    user = CardUser.objects.get(pk=pk)
    message, u_success = '', False
    context = {
        'c_title': 'Update User',
        'u': user,
        'form': UserForm(instance=user),
        'upd': user.id
    }
    if request.method == 'POST':
        form = UserForm(instance=user, data=request.POST or None)
        if form.is_valid():
            form.save()
            message = '<i class="fa fa-check"></i>'
            u_success = True
        else:
            message = '<i class="fa fa-remove"></i>'
        context['message'] = message
        context['u_success'] = u_success
        return render(request, 'users/user_management_tr_partial.html', context)
    return render(request, 'users/user_management_form_partial.html', context)


class UserDetail(LoginRequiredMixin, DetailView):
    model = CardUser
    template_name = 'users/user_update.html'

    def get_object(self, queryset=None):
        return CardUser.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        user = self.get_object()
        data = super().get_context_data()
        data['title'] = '%s %s' % (user.first_name, user.last_name)
        data['object'] = user
        data['form'] = UserForm(instance=user)
        data['my_id'] = user.id
        data['c_title'] = 'Update User'
        return data


class UserUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CardUser
    template_name = 'users/user_update.html'
    form_class = UserForm
    context_object_name = 'obj'
    success_message = 'User updated successfully'

    def get_object(self, **kwargs):
        return CardUser.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'Update User Profile'
        data['obj'] = self.context_object_name
        data['object'] = self.get_object()
        return data

    def get_success_url(self):
        return reverse('users:user-profile', kwargs={'pk': self.kwargs.get('pk')})


@login_required(login_url='/users/')
def user_update(request, pk):
    user = CardUser.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserForm(instance=user, data=request.POST or None)
        if form.is_valid():
            form.save()
            message = '<i class="fa fa-check"></i> Success'
        else:
            message = '<i class="fa fa-remove"></i> Error'
            print(form.errors)
        return render(request, 'users/user_detail_card_partial.html',
                      {'object': user, 'message': message})
    return render(request, 'users/user_form_template.html',
                  {'my_id': pk, 'form': UserForm(instance=user)})


@login_required(login_url='/users/')
def password_update(request, pk: int):
    user = CardUser.objects.get(pk=pk)
    if request.method == 'POST':
        form = SetPasswordForm(user, data=request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated successfully')
            return redirect('users:user-update', pk)
        else:
            messages.warning(request, form.errors)
    form = SetPasswordForm(user)
    return render(request, 'users/user_update.html',
                  {'title': 'Update Password', 'form': form, 'object': user, 'c_title': 'Reset password'}
                  )


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
