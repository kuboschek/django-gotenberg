from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage as storage
from django.contrib.staticfiles import finders

from pdftemplates import render

class Command(BaseCommand):
    help = 'Test extraction of static files from templates'

    def handle(self, *args, **options):
        with open('cows.pdf', 'wb') as f:
            pdf = render.to_pdf('pdftemplates/cows.html', {'test': 'If you see this text, it works!'})
            f.write(pdf)