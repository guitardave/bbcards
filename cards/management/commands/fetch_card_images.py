from django.core.management.base import BaseCommand

from cards.image_agent import find_image_for_card
from cards.models import Card


class Command(BaseCommand):
    help = 'Use the AI image agent to find images for cards that have none.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=25, help='Max cards to process (default 25)')
        parser.add_argument('--overwrite', action='store_true', help='Also replace existing images')

    def handle(self, *args, **opts):
        qs = Card.objects.select_related('player_id', 'card_set_id').order_by('id')
        if not opts['overwrite']:
            qs = qs.filter(card_image__isnull=True) | qs.filter(card_image='')
        found = 0
        for card in qs[:opts['limit']]:
            try:
                url = find_image_for_card(card, overwrite=opts['overwrite'])
            except Exception as e:
                self.stderr.write(f'[{card.pk}] error: {e}')
                continue
            if url:
                found += 1
                self.stdout.write(self.style.SUCCESS(f'[{card.pk}] {card.slug} <- {url}'))
            else:
                self.stdout.write(f'[{card.pk}] {card.slug}: no image found')
        self.stdout.write(f'Done. {found} image(s) saved.')
