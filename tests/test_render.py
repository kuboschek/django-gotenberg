"""
Integration tests for django_gotenberg.render_to_pdf.

These tests require a running Gotenberg instance at DJANGO_GOTENBERG_HOST.
Run with: DJANGO_GOTENBERG_HOST=http://localhost:3000 python -m pytest tests/ -v
"""
import os

import django
import pytest
from django.http import HttpResponse
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testbed.settings")
django.setup()

from django_gotenberg import render_to_pdf
from django_gotenberg.exceptions import GotenbergException

requires_gotenberg = pytest.mark.skipif(
    not os.environ.get("DJANGO_GOTENBERG_HOST"),
    reason="DJANGO_GOTENBERG_HOST not set; skipping tests that require a running Gotenberg instance",
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


def test_render_to_pdf_raises_when_host_missing(request_factory, monkeypatch):
    """render_to_pdf raises GotenbergException when DJANGO_GOTENBERG_HOST is not set."""
    monkeypatch.delenv("DJANGO_GOTENBERG_HOST", raising=False)
    request = request_factory.get("/")
    with pytest.raises(GotenbergException, match="DJANGO_GOTENBERG_HOST"):
        render_to_pdf(request, "test.html")
