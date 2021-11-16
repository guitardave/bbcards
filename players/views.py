from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from .models import Player
from .forms import PlayerForm


class PlayerList(ListView):
	model = Player
	template_name = 'players/player_list.html'
	context_object_name = 'players'

	def get_queryset(self):
		return Player.objects.all().order_by('player_lname')

	def get_context_data(self, *, object_list=None, **kwargs):
		data = super(PlayerList, self).get_context_data(**kwargs)
		data['title'] = 'Player List'
		data['players'] = self.get_queryset()
		return data


class PlayerDetail(DetailView):
	model = Player
	template_name = 'players/player_detail.html'

	def get_context_data(self, **kwargs):
		obj = Player.objects.get(slug=self.kwargs['slug'])
		data = super(PlayerDetail, self).get_context_data(**kwargs)
		data['title'] = '{} {}'.format(obj.player_fname, obj.player_lname)
		data['object'] = obj
		return data


class PlayerNew(LoginRequiredMixin, CreateView):
	model = Player
	template_name = 'players/player_form.html'
	form_class = PlayerForm
	context_object_name = 'out'

	def get_context_data(self, **kwargs):
		data = super(PlayerNew, self).get_context_data(**kwargs)
		data['title'] = 'Add New Player'
		data['out'] = self.context_object_name
		return data


class PlayerUpdate(LoginRequiredMixin, UpdateView):
	model = Player
	template_name = 'players/player_form.html'
	form_class = PlayerForm
	context_object_name = 'out'

	def get_context_data(self, **kwargs):
		obj = Player.objects.get(slug=self.kwargs['slug'])
		data = super(PlayerUpdate, self).get_context_data(**kwargs)
		data['title'] = 'Update Player - ' + '{} {}'.format(obj.player_fname, obj.player_lname)
		data['out'] = self.context_object_name
		return data
