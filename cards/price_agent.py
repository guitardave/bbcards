"""
AI agent that looks up current market pricing for a Card.

The LLM (DigitalOcean Serverless Inference, OpenAI-compatible API) drives two tools:
  - search_web:   Brave Web Search (titles, URLs and snippets - sold listings, price guides, etc.)
  - record_price: submit the low / typical / high USD price found, plus a source URL and note
"""
import json
import logging
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.utils import timezone

from .image_agent import HTTP_TIMEOUT, ImageAgentError, _chat, card_description
from .models import Card

logger = logging.getLogger(__name__)

MAX_STEPS = 6

SYSTEM_PROMPT = (
    'You research the current market value of a specific sports trading card in USD. '
    'Use search_web (refine the query at most twice) looking for recent sold listings (eBay sold, '
    '130point, COMC) and price guides. Base prices only on figures that appear in the search results; '
    'never invent numbers. Account for the condition/grade if one is given. Then call record_price with '
    'the low, typical and high price and the url of the best source. If no credible price is found, '
    'reply with the single word NONE.'
)

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'search_web',
            'description': 'Search the web. Returns a list of {url, title, snippet}.',
            'parameters': {
                'type': 'object',
                'properties': {'query': {'type': 'string'}},
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'record_price',
            'description': 'Record the price found. All prices in USD. source_url must come from search_web results.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'low': {'type': 'number'},
                    'typical': {'type': 'number'},
                    'high': {'type': 'number'},
                    'source_url': {'type': 'string'},
                    'notes': {'type': 'string', 'description': 'One short sentence, e.g. "avg of 5 eBay sales, last 30 days"'},
                },
                'required': ['typical', 'source_url'],
            },
        },
    },
]


def search_web(query: str, count: int = 10) -> list[dict]:
    key = getattr(settings, 'BRAVE_API_KEY', None)
    if not key:
        raise ImageAgentError('BRAVE_API_KEY is not set')
    resp = requests.get(
        'https://api.search.brave.com/res/v1/web/search',
        params={'q': query, 'count': count},
        headers={'X-Subscription-Token': key, 'Accept': 'application/json'},
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return [
        {'url': r.get('url', ''), 'title': r.get('title', ''),
         'snippet': ' '.join([r.get('description', '')] + (r.get('extra_snippets') or []))[:600]}
        for r in resp.json().get('web', {}).get('results', []) if r.get('url')
    ]


def _money(value) -> Decimal | None:
    try:
        d = Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return d if 0 < d < Decimal('100000000') else None


def find_price_for_card(card: Card) -> bool:
    """Run the agent for one card. Saves the price on the card and returns True, or False if none was found."""
    desc = card_description(card)
    if card.condition:
        desc += f' (condition: {card.condition})'
    if card.graded:
        desc += ' (graded)'
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f'Find the current market price of this card: {desc}'},
    ]
    seen_urls: set[str] = set()

    for _step in range(MAX_STEPS):
        msg = _chat(messages, TOOLS)
        messages.append({k: v for k, v in msg.items() if v is not None})
        calls = msg.get('tool_calls') or []
        if not calls:
            return False  # model answered NONE (or gave up)

        for call in calls:
            name = call['function']['name']
            try:
                args = json.loads(call['function'].get('arguments') or '{}')
            except json.JSONDecodeError:
                args = {}
            if name == 'search_web':
                try:
                    results = search_web(str(args.get('query', '')))
                    seen_urls.update(r['url'] for r in results)
                    output = json.dumps(results)
                except Exception as e:
                    output = json.dumps({'error': str(e)})
            elif name == 'record_price':
                typical = _money(args.get('typical'))
                low = _money(args.get('low')) or typical
                high = _money(args.get('high')) or typical
                url = str(args.get('source_url', ''))
                if typical is None:
                    output = json.dumps({'error': 'typical must be a positive number'})
                elif url not in seen_urls:
                    output = json.dumps({'error': 'source_url was not in search results'})
                else:
                    card.price_estimate, card.price_low, card.price_high = typical, min(low, typical), max(high, typical)
                    card.price_source = url[:500]
                    card.price_notes = str(args.get('notes', ''))[:300]
                    card.price_checked_at = timezone.now()
                    card.save(update_fields=['price_estimate', 'price_low', 'price_high',
                                             'price_source', 'price_notes', 'price_checked_at'])
                    logger.info('Saved price $%s for card %s from %s', typical, card.pk, url)
                    return True
            else:
                output = json.dumps({'error': f'unknown tool {name}'})
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': output})
    return False
