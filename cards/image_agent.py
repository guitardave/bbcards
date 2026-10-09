"""
AI agent that finds and attaches an image for a Card.

The LLM (DigitalOcean Serverless Inference, OpenAI-compatible API) drives two tools:
  - search_images: Brave Image Search
  - choose_image:  pick a result URL; the URL is downloaded, validated and saved to Card.card_image
"""
import ipaddress
import json
import logging
import socket
from io import BytesIO
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from .models import Card

logger = logging.getLogger(__name__)

MAX_STEPS = 6
MAX_IMAGE_BYTES = 8 * 1024 * 1024
HTTP_TIMEOUT = 20

SYSTEM_PROMPT = (
    'You find a photo of a specific sports trading card. Use search_images (refine the query '
    'at most twice if results look wrong), then call choose_image with the url of the best result. '
    'Prefer a clear, front-facing image of the actual card (same player, year, set and card number). '
    'If nothing plausible is found, reply with the single word NONE.'
)

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'search_images',
            'description': 'Search the web for images. Returns a list of {url, title, source}.',
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
            'name': 'choose_image',
            'description': 'Select the best image. The url must come from search_images results.',
            'parameters': {
                'type': 'object',
                'properties': {'url': {'type': 'string'}, 'reason': {'type': 'string'}},
                'required': ['url'],
            },
        },
    },
]


class ImageAgentError(Exception):
    pass


def card_description(card: Card) -> str:
    parts = [
        card.card_set_id.year,
        card.card_set_id.card_set_name,
        card.card_set_id.sport,
        card.card_subset,
        f'#{card.card_num}',
        f'{card.player_id.player_fname} {card.player_id.player_lname}',
    ]
    return ' '.join(str(p) for p in parts if p)


def _is_public_url(url: str) -> bool:
    """Reject non-http(s) URLs and hosts resolving to private/loopback addresses (SSRF guard)."""
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        return False
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or 443)
    except socket.gaierror:
        return False
    return all(ipaddress.ip_address(i[4][0]).is_global for i in infos)


def search_images(query: str, count: int = 10) -> list[dict]:
    key = getattr(settings, 'BRAVE_API_KEY', None)
    if not key:
        raise ImageAgentError('BRAVE_API_KEY is not set')
    resp = requests.get(
        'https://api.search.brave.com/res/v1/images/search',
        params={'q': query, 'count': count, 'safesearch': 'strict'},
        headers={'X-Subscription-Token': key, 'Accept': 'application/json'},
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    results = []
    for r in resp.json().get('results', []):
        url = (r.get('properties') or {}).get('url')
        if url:
            results.append({'url': url, 'title': r.get('title', ''), 'source': r.get('source', '')})
    return results


def download_image(url: str) -> tuple[bytes, str]:
    """Download and validate an image; returns (bytes, extension)."""
    if not _is_public_url(url):
        raise ImageAgentError('URL is not a public http(s) address')
    with requests.get(url, stream=True, timeout=HTTP_TIMEOUT, allow_redirects=False,
                      headers={'User-Agent': 'bbcards-image-agent/1.0'}) as resp:
        resp.raise_for_status()
        data = BytesIO()
        for chunk in resp.iter_content(64 * 1024):
            data.write(chunk)
            if data.tell() > MAX_IMAGE_BYTES:
                raise ImageAgentError('Image too large')
    try:
        img = Image.open(BytesIO(data.getvalue()))
        img.verify()
        fmt = (img.format or '').lower()
    except Exception as e:
        raise ImageAgentError(f'Not a valid image: {e}')
    if fmt not in ('jpeg', 'png', 'webp', 'gif'):
        raise ImageAgentError(f'Unsupported image format: {fmt}')
    return data.getvalue(), 'jpg' if fmt == 'jpeg' else fmt


def _chat(messages: list[dict]) -> dict:
    key = getattr(settings, 'MODEL_ACCESS_KEY', None)
    if not key:
        raise ImageAgentError('MODEL_ACCESS_KEY is not set')
    resp = requests.post(
        f'{settings.DO_INFERENCE_URL}/chat/completions',
        headers={'Authorization': f'Bearer {key}'},
        json={'model': settings.DO_INFERENCE_MODEL, 'messages': messages, 'tools': TOOLS, 'temperature': 0},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']


def find_image_for_card(card: Card, overwrite: bool = False) -> str | None:
    """Run the agent for one card. Returns the source URL saved, or None if nothing was found."""
    if card.card_image and not overwrite:
        return None

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f'Find an image of this card: {card_description(card)}'},
    ]
    seen_urls: set[str] = set()

    for _ in range(MAX_STEPS):
        msg = _chat(messages)
        messages.append({k: v for k, v in msg.items() if v is not None})
        calls = msg.get('tool_calls') or []
        if not calls:
            return None  # model answered NONE (or gave up)

        for call in calls:
            name = call['function']['name']
            try:
                args = json.loads(call['function'].get('arguments') or '{}')
            except json.JSONDecodeError:
                args = {}
            if name == 'search_images':
                try:
                    results = search_images(str(args.get('query', '')))
                    seen_urls.update(r['url'] for r in results)
                    output = json.dumps(results)
                except Exception as e:
                    output = json.dumps({'error': str(e)})
            elif name == 'choose_image':
                url = str(args.get('url', ''))
                if url not in seen_urls:
                    output = json.dumps({'error': 'url was not in search results'})
                else:
                    try:
                        data, ext = download_image(url)
                    except Exception as e:
                        output = json.dumps({'error': f'download failed: {e}; choose another'})
                    else:
                        card.card_image.save(f'{card.slug}.{ext}', ContentFile(data), save=True)
                        logger.info('Saved image for card %s from %s', card.pk, url)
                        return url
            else:
                output = json.dumps({'error': f'unknown tool {name}'})
            messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': output})
    return None
