def toggle_mode_ctx(request):
    if 'toggle_mode' in request.COOKIES and request.COOKIES['toggle_mode'] == 'dark':
        return {'mode': 'dark'}
    else:
        return {'mode': None}


def user_full_name_ctx(request):
    return {'user_full_name': '%s %s' % (request.user.first_name, request.user.last_name)}
