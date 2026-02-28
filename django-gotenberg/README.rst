=================
Django Gotenberg
=================

Django Gotenberg is a Django app that provides a ``render_to_pdf`` function to
render Django templates to PDF responses using a `Gotenberg <https://gotenberg.dev>`_ instance.

Quick start
-----------

1. Run a Gotenberg instance::

    docker run --rm -p 3000:3000 gotenberg/gotenberg:8

2. Set the ``DJANGO_GOTENBERG_HOST`` environment variable::

    export DJANGO_GOTENBERG_HOST=http://localhost:3000

3. Use ``render_to_pdf`` in your views::

    from django_gotenberg import render_to_pdf

    def my_view(request):
        return render_to_pdf(request, 'my_template.html', {'key': 'value'})

    # With a download filename:
    def my_download_view(request):
        return render_to_pdf(request, 'my_template.html', filename='report.pdf')

Configuration
-------------

All configuration is done via environment variables with the ``DJANGO_GOTENBERG_`` prefix:

============================================ ========================================= =========================================
Variable                                     Description                               Default
============================================ ========================================= =========================================
``DJANGO_GOTENBERG_HOST``                    URL of the Gotenberg instance (required)  —
``DJANGO_GOTENBERG_TIMEOUT``                 Request timeout in seconds                ``30.0``
``DJANGO_GOTENBERG_USERNAME``                HTTP basic auth username                  —
``DJANGO_GOTENBERG_PASSWORD``                HTTP basic auth password                  —
============================================ ========================================= =========================================
