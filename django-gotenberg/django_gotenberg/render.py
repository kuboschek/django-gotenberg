import os

from django.http import HttpResponse
from django.template import loader
from httpx import BasicAuth, HTTPError
from gotenberg_client import GotenbergClient

from . import exceptions

_ENV_PREFIX = "DJANGO_GOTENBERG_"


def _get_client() -> GotenbergClient:
    host = os.environ.get(_ENV_PREFIX + "HOST")
    if not host:
        raise exceptions.GotenbergException(
            "DJANGO_GOTENBERG_HOST environment variable must be set to the URL of your Gotenberg instance."
        )

    timeout = float(os.environ.get(_ENV_PREFIX + "TIMEOUT", 30.0))

    username = os.environ.get(_ENV_PREFIX + "USERNAME")
    password = os.environ.get(_ENV_PREFIX + "PASSWORD")

    auth = BasicAuth(username, password) if username and password else None

    return GotenbergClient(host, timeout=timeout, auth=auth)


def render_to_pdf(request, template_name, context=None, filename=None):
    """
    Render a Django template to a PDF HTTP response using Gotenberg.

    Args:
        request: The current HttpRequest.
        template_name: Name of the template to render.
        context: Optional dict of context variables.
        filename: Optional filename for the Content-Disposition header.

    Returns:
        HttpResponse with content-type 'application/pdf'.
    """
    if context is None:
        context = {}

    t = loader.get_template(template_name)
    html = t.render(context, request)

    try:
        with _get_client() as client:
            with client.chromium.html_to_pdf() as route:
                route.string_index(html)
                response = route.run()
                pdf_content = response.content
    except HTTPError as e:
        raise exceptions.GotenbergException(e) from e

    http_response = HttpResponse(pdf_content, content_type="application/pdf")

    if filename:
        # Sanitize filename: strip path components and encode for the header
        safe_name = os.path.basename(filename).replace('"', '\\"').replace("\n", "").replace("\r", "")
        http_response["Content-Disposition"] = 'attachment; filename="{}"'.format(safe_name)

    return http_response
