from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from .models import Player
from .forms import PlayerForm


class PlayerList(ListView):
	model = Player
	template_name = 'players/player_list.html'
	context_object_name = 'players'
	paginate_by = 30
	ordering = 'player_lname'

	def get_context_data(self, *, object_list=None, **kwargs):
		data = super(PlayerList, self).get_context_data(**kwargs)
		data['title'] = 'Player List'
		data['players'] = self.get_queryset()
		data['form'] = PlayerForm()
		return data

	def post(self, *args, **kwargs):
		form = PlayerForm(self.request.POST)
		if form.is_valid():
			form.save()
			messages.success(self.request, 'Your player was successfully saved.')
			return redirect('players:players-home')


class PlayerDetail(DetailView):
	model = Player
	template_name = 'players/player_detail.html'

	def get_instance(self):
		return Player.objects.get(slug=self.kwargs['slug'])

	def get_context_data(self, **kwargs):
		obj = self.get_instance()
		data = super(PlayerDetail, self).get_context_data(**kwargs)
		data['title'] = '{} {}'.format(obj.player_fname, obj.player_lname)
		data['object'] = obj
		data['form'] = PlayerForm(instance=obj)
		return data

	def post(self, *args, **kwargs):
		form = PlayerForm(self.request.POST, instance=self.get_instance())
		if form.is_valid():
			form.save()
			messages.success(self.request, 'Player was successfully saved.')
			return redirect('players:players-det', slug=kwargs['slug'])


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


def player_add(request):
	if request.method == 'POST':
		pass
	return render(request, '', {})


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
