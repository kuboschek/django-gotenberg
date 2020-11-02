from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage as storage
from django.contrib.staticfiles import finders

import pdftemplates
class Command(BaseCommand):
    help = 'Test extraction of static files from templates'

    def handle(self, *args, **options):
        with open('cows.pdf', 'wb') as f:
            pdftemplates.render_to_file('pdftemplates/cows.html', f, {'test': 'If you see this text, it works!'})