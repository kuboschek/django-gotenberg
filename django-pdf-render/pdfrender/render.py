import os
import requests
import mimetypes
from io import BytesIO

from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.template.base import NodeList, TextNode
from django.templatetags.static import StaticNode
from django.template.defaulttags import URLNode
from django.contrib.staticfiles.storage import staticfiles_storage as storage
from django.contrib.staticfiles import finders


from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.http import HttpResponse

from . import exceptions

PATH_SEP_REPLACER = "-"

try:
    RENDER_SERVER_URL = settings.PDF_RENDER_SERVER
except AttributeError:
    raise ImproperlyConfigured("PDF_RENDER_SERVER needs to be set to the URL of the PDF render server you're using.")

def _flatten(path):
    return path.replace('/', PATH_SEP_REPLACER)

def _resolve_absolute(path):
    if settings.DEBUG:
        absolute_path = finders.find(path)
        if not absolute_path:
            raise exceptions.FileGatheringException("File '%s' could not be found" % path)
        return absolute_path
    else:
        return storage.path(path)
        
def _to_bytes(template_name, context={}):
    t = loader.get_template(template_name)

    file_map = {} # Map from flattened path from static tag -> absolute file system file path

    new_nodes = NodeList()

    for node in t.template:
        if node.__class__ == StaticNode:
            orig_path = node.path.resolve(context)
            flat_path = _flatten(orig_path)
            file_map[flat_path] = _resolve_absolute(orig_path)
            node = TextNode(flat_path)

        new_nodes.append(node)

    t.template.nodelist = new_nodes
    rendered_html = t.render(context)


    try:
        files = [
            ('files', ('index.html', rendered_html, 'text/html'))
        ]

        for flat_path, fs_path in file_map.items():
            files.append(
                ('files', (flat_path, open(fs_path, 'rb'), mimetypes.guess_type(flat_path)[0] or 'application/octet-stream'))
            )

        r = requests.post(RENDER_SERVER_URL, files=files)
        r.raise_for_status()

        return r.content

    except requests.exceptions.RequestException as e:
        raise exceptions.PDFServerException(e)

    except OSError as e:
        raise exceptions.FileGatheringException(e)

def _to_response(template_name, context={}, filename=None):
    response = HttpResponse(_to_bytes(template_name, context), content_type='application/pdf')

    if filename:
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response


def _to_file(template_name, file, context={}):
    file.write(_to_bytes(template_name, context))