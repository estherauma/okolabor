import threading

_user = threading.local()

def get_current_user():
    user = getattr(_user, 'value', None)
    print("DEBUG :: Current user from middleware =>", user)
    return user


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        response = self.get_response(request)
        return response
