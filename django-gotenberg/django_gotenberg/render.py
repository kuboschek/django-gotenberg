import os
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage as storage
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.template import loader
from django.template.base import NodeList, TextNode
from django.templatetags.static import StaticNode
from httpx import BasicAuth, HTTPError
from gotenberg_client import GotenbergClient

from . import exceptions

_PATH_SEP_REPLACER = "-"


def _flatten(path):
    """Replace path separators so the filename is safe to use as a Gotenberg resource name."""
    return _PATH_SEP_REPLACER.join(Path(str(path)).parts)


def _resolve_absolute(path):
    """Return the absolute filesystem path for a static-file path."""
    if settings.DEBUG:
        absolute_path = finders.find(path)
        if not absolute_path:
            raise exceptions.FileGatheringException("File '%s' could not be found" % path)
        return absolute_path
    else:
        return storage.path(path)


def _get_client() -> GotenbergClient:
    host = getattr(settings, "GOTENBERG_HOST", None)
    if not host:
        raise ImproperlyConfigured(
            "GOTENBERG_HOST must be set in your Django settings to the URL of your Gotenberg instance."
        )

    timeout = float(getattr(settings, "GOTENBERG_TIMEOUT", 30.0))

    username = getattr(settings, "GOTENBERG_USERNAME", None)
    password = getattr(settings, "GOTENBERG_PASSWORD", None)

    auth = BasicAuth(username, password) if username and password else None

    return GotenbergClient(host, timeout=timeout, auth=auth)


def render_to_pdf(request, template_name, context=None, filename=None):
    """
    Render a Django template to a PDF HTTP response using Gotenberg.

    Static files referenced via ``{% static %}`` tags in the template's
    top-level node list are resolved on the filesystem and sent to Gotenberg
    alongside the rendered HTML so that images, stylesheets, and other assets
    are available during PDF generation.

    Args:
        request: The current HttpRequest.
        template_name: Name of the template to render.
        context: Optional dict of context variables.
        filename: Optional filename for the Content-Disposition header.

    Returns:
        HttpResponse with content-type 'application/pdf'.

    Raises:
        ImproperlyConfigured: When GOTENBERG_HOST is not set in Django settings.
        exceptions.FileGatheringException: When a referenced static file cannot be found.
        exceptions.GotenbergException: When the Gotenberg HTTP request fails.
    """
    if context is None:
        context = {}

    t = loader.get_template(template_name)

    # Walk the template's top-level node list and collect StaticNode references.
    # file_map: flat resource name -> absolute filesystem path
    file_map = {}
    new_nodes = NodeList()
    original_nodelist = t.template.nodelist

    for node in original_nodelist:
        if isinstance(node, StaticNode):
            orig_path = node.path.resolve(context)
            flat_path = _flatten(orig_path)
            file_map[flat_path] = _resolve_absolute(orig_path)
            node = TextNode(flat_path)
        new_nodes.append(node)

    t.template.nodelist = new_nodes
    try:
        html = t.render(context, request)
    finally:
        t.template.nodelist = original_nodelist

    try:
        with _get_client() as client:
            with client.chromium.html_to_pdf() as route:
                route.string_index(html)
                for flat_path, fs_path in file_map.items():
                    route.resource(Path(fs_path), name=flat_path)
                response = route.run()
                pdf_content = response.content
    except HTTPError as e:
        raise exceptions.GotenbergException(e) from e
    except OSError as e:
        raise exceptions.FileGatheringException(e) from e

    http_response = HttpResponse(pdf_content, content_type="application/pdf")

    if filename:
        # Sanitize filename: strip path components and encode for the header
        safe_name = os.path.basename(filename).replace('"', '\\"').replace("\n", "").replace("\r", "")
        http_response["Content-Disposition"] = 'attachment; filename="{}"'.format(safe_name)

    return http_response
