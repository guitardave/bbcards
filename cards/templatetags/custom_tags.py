import datetime
import re
from typing import Any

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="mod")
def modulus(val1, val2):
    try:
        return val1 % val2
    except ValueError or TypeError:
        return ''
