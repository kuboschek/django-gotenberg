import os
import requests
import mimetypes
from io import BytesIO

from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.template.base import NodeList, TextNode
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage as storage
from django.contrib.staticfiles import finders


from django.conf import settings

PATH_SEP_REPLACER = "-"

def _flatten(path):
    return path.replace('/', PATH_SEP_REPLACER)

def _resolve_absolute(path):
    if settings.DEBUG:
        absolute_path = finders.find(path)
        if not absolute_path:
            raise Error("'%s' could not be found" % path)
        return absolute_path
    else:
        return storage.path(path)

def to_pdf(template_name, context={}):
    t = loader.get_template(template_name)

    file_map = {} # Map from staticfile path -> flattened filename

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

    multiple_files = [
        ('files', ('index.html', rendered_html, 'text/html'))
    ]

    for flat_path, fs_path in file_map.items():
        multiple_files.append(
            ('files', (flat_path, open(fs_path, 'rb'), mimetypes.guess_type(flat_path)[0] or 'application/octet-stream'))
        )

    url = 'http://localhost:3000'

    r = requests.post(url, files=multiple_files)
    return r.content

