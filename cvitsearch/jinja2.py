from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from jinja2 import Environment

from django.utils.timezone import template_localtime

import os


def basename(path):
    return os.path.basename(path)


def dirname(path):
    return os.path.dirname(path)


def environment(**options):
    env = Environment(extensions=[], **options)
    env.filters['localtime'] = template_localtime
    env.filters['basename'] = basename
    env.filters['dirname'] = dirname
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'messages': messages.get_messages,
        'MEDIA_URL': settings.MEDIA_URL
    })
    return env