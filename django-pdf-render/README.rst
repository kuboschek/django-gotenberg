=================
Django PDF Render
=================

PDF Render is a Django app that provides functions to
render PDF files from Django templates.

To do so, it bundles all files required for template rendering 
and sends them to a separate `server <https://github.com/kuboschek/pdf-render-server>`_ 
for processing. Using Chromium on a separate server ensures PDFs 
that are consistent with browser-rendered templates.

Quick start
-----------

1. Run a pdf-render-server::

    docker run -p 3000:3000 kuboschek/pdf-render-server


2. Add PDF_RENDER_SERVER to your settings::

    PDF_RENDER_SERVER = 'http://localhost:3000'

3. Use the functions from 'pdfrender' to render PDFs in your views::

    pdfrender.render_to_bytes(template_name, context)
    pdfrender.render_to_response(template_name, context, filename=None)
    pdfrender.render_to_file(template_name, fp, context)


