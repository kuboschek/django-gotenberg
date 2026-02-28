from django_gotenberg import render_to_pdf


def example(request):
    return render_to_pdf(request, 'test.html', {'title': 'It works!', 'subtitle': 'If you can read this, it works.'})