from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from urllib.request import urlopen
import json


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
            messages.info(request, 'Login Failed')
            context['form'] = AuthenticationForm()
    else:
        context['form'] = AuthenticationForm()
    return render(request, 'users/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'logout successful')
    return HttpResponseRedirect('/users/')


def weather(request):
    API_URI = "http://api.weatherapi.com/v1/current.json?key=fdab2f8d0cb3412395503740211006&q=75056&aqi=no"
    with urlopen(API_URI) as response:
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
             f'and {cond} with winds of {wind} (gusts up to {wind_g}) in {loc}, {st}'

    return render(request, 'users/weather.html', {'title': 'Weather Information', 'report': report})
