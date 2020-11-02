import pdfrender

def example(request):
    return pdfrender.render_to_response('test.html', {'title': 'It works!', 'subtitle': 'If you can read this, it works.'})