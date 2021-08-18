from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)


class PlayerList(ListView):
	model = Player
	template_name = ''
	context_object_name = 'players'

	def get_queryset(self):
		return Player.objects.all().order_by('player_lname')

	def get(self, request, *args, **kwargs):
		context = {'title': 'Player List', 'players': self.get_queryset()}
		return render(request, self.template_name, context)



class PlayerDetail(DetailView):
	model = Player
	template_name = 'player-detail.html'

	def get_queryset(self):
		return Player.objects.get(pk=self.kwargs.get('pk'))

	def get(self, request, *args, **kwargs):
		context = {'title': 'Player Detail', 'object': self.get_queryset()}
		return render(request, self.template_name, context)


class PlayerNew(CreateView):
	model = PlayerNew
	template_name = 'players/player-form.html'
	form_class = PlayerForm


