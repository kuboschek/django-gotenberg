from . import render_to_response


def test_render(request):
    return render_to_response('pdftemplates/cows.html', context={
        'test': 'If you see this text, it works!'
    })