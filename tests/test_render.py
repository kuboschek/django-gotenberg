"""
Integration tests for django_gotenberg.render_to_pdf.

These tests require a running Gotenberg instance configured via the
GOTENBERG_HOST Django setting (set in testbed/settings.py).
Run with: python -m pytest tests/ -v
"""
import os

import django
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testbed.settings")
django.setup()

from django_gotenberg import render_to_pdf
from django_gotenberg.exceptions import FileGatheringException, GotenbergException

requires_gotenberg = pytest.mark.skipif(
    not os.environ.get("GOTENBERG_HOST"),
    reason="GOTENBERG_HOST env var not set; skipping tests that require a running Gotenberg instance",
)


@pytest.fixture
def request_factory():
    return RequestFactory()


@requires_gotenberg
def test_render_to_pdf_returns_http_response(request_factory):
    """render_to_pdf returns an HttpResponse with PDF content type."""
    request = request_factory.get("/")
    response = render_to_pdf(request, "test.html", {"title": "Test", "subtitle": "Sub"})
    assert isinstance(response, HttpResponse)
    assert response["Content-Type"] == "application/pdf"


@requires_gotenberg
def test_render_to_pdf_content_is_pdf(request_factory):
    """render_to_pdf response content begins with the PDF magic bytes."""
    request = request_factory.get("/")
    response = render_to_pdf(request, "test.html", {"title": "Test", "subtitle": "Sub"})
    assert response.content[:4] == b"%PDF"


@requires_gotenberg
def test_render_to_pdf_with_filename(request_factory):
    """render_to_pdf sets Content-Disposition when filename is given."""
    request = request_factory.get("/")
    response = render_to_pdf(request, "test.html", filename="report.pdf")
    assert "Content-Disposition" in response
    assert "report.pdf" in response["Content-Disposition"]


@requires_gotenberg
def test_render_to_pdf_without_filename_no_disposition(request_factory):
    """render_to_pdf does not set Content-Disposition when filename is omitted."""
    request = request_factory.get("/")
    response = render_to_pdf(request, "test.html")
    assert "Content-Disposition" not in response


@override_settings(GOTENBERG_HOST=None)
def test_render_to_pdf_raises_when_host_missing(request_factory):
    """render_to_pdf raises ImproperlyConfigured when GOTENBERG_HOST is not set."""
    request = request_factory.get("/")
    with pytest.raises(ImproperlyConfigured, match="GOTENBERG_HOST"):
        render_to_pdf(request, "test.html")
