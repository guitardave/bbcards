from django.test import TestCase, RequestFactory
from django.urls import reverse
from players.models import Player
from cards.models import CardSet, Card
from users.models import CardUser
from cards.views import card_list_last_n, card_set_list, card_image
from players.views import player_list
from users.views import login_view, toggle_view_mode, UserDetail, user_management_list


class PresentationViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.player = Player.objects.create(
            player_fname='Hank',
            player_lname='Aaron'
        )
        self.user = CardUser.objects.create_superuser(
            username='testcollector',
            email='test@example.com',
            password='Password123!',
            first_name='Mickey',
            last_name='Mantle',
            favorite_player=self.player
        )
        self.card_set = CardSet.objects.create(
            year=1954,
            card_set_name='Topps',
            sport='Baseball'
        )
        self.card = Card.objects.create(
            player_id=self.player,
            card_set_id=self.card_set,
            card_num='128',
            card_subset='Rookie'
        )

    def test_cards_list_50_view(self):
        request = self.factory.get(reverse('cards:card-list-50'))
        request.user = self.user
        request.COOKIES = {}
        response = card_list_last_n(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('BBCARDS', content)
        self.assertIn('Hank Aaron', content)
        self.assertIn('Topps', content)
        self.assertIn('sports-navbar', content)
        self.assertIn('sports-accent-bar', content)
        self.assertIn('brand-logo', content)
        self.assertIn('baseball_logo_black_background.jpg', content)
        self.assertIn('sports-search-btn', content)
        self.assertIn('sports-search-input', content)

    def test_static_assets_finders(self):
        from django.contrib.staticfiles import finders
        self.assertIsNotNone(finders.find('pub/css/custom.css'))
        self.assertIsNotNone(finders.find('pub/css/main.css'))
        self.assertIsNotNone(finders.find('pub/img/baseball_logo_black_background.jpg'))
        self.assertIsNotNone(finders.find('cards/fonts/OldSport02AthleticNcv-E0gj.ttf'))

    def test_cardsets_view(self):
        request = self.factory.get(reverse('cards:cardsets', kwargs={'n_count': 50}))
        request.user = self.user
        request.COOKIES = {}
        response = card_set_list(request, n_count=50)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Topps', content)
        self.assertIn('Baseball', content)
        self.assertIn('sport-badge-baseball', content)

    def test_players_view(self):
        request = self.factory.get(reverse('players:players-home', kwargs={'n_list': 50}))
        request.user = self.user
        request.COOKIES = {}
        response = player_list(request, n_list=50)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Hank', content)
        self.assertIn('Aaron', content)

    def test_card_image_slab_view(self):
        request = self.factory.get(reverse('cards:card-image', kwargs={'slug': self.card.slug}))
        request.user = self.user
        request.COOKIES = {}
        response = card_image(request, slug=self.card.slug)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('graded-slab', content)
        self.assertIn('BBCards Authentic Vault Slab', content)

    def test_user_detail_view(self):
        request = self.factory.get(reverse('users:user-profile', kwargs={'pk': self.user.id}))
        request.user = self.user
        request.COOKIES = {}
        view = UserDetail.as_view()
        response = view(request, pk=self.user.id)
        self.assertEqual(response.status_code, 200)
        content = response.rendered_content
        self.assertIn('Mickey Mantle', content)
        self.assertIn('Favorite Player', content)

    def test_user_management_view(self):
        request = self.factory.get(reverse('users:user-management'))
        request.user = self.user
        request.COOKIES = {}
        response = user_management_list(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('User Management', content)
        self.assertIn('Active Roster', content)

    def test_login_page_renders_sports_theme(self):
        request = self.factory.get(reverse('users:login'))
        request.user = self.user
        request.COOKIES = {}
        response = login_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Clubhouse Access', content)
        self.assertIn('Enter Vault', content)

    def test_toggle_mode(self):
        request = self.factory.get(reverse('users:toggle_mode', kwargs={'mode': 'dark'}))
        request.user = self.user
        request.COOKIES = {}
        response = toggle_view_mode(request, mode='dark')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies['toggle_mode'].value, 'dark')
