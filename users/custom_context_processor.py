def toggle_mode_ctx(request):
    if 'toggle_mode' in request.COOKIES and request.COOKIES['toggle_mode'] == 'dark':
        return {'mode': 'dark'}
    else:
        return {'mode': None}
