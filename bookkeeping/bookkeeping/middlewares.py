from django.utils.deprecation import MiddlewareMixin

class NoCSRFCheck(MiddlewareMixin):
    print("NoCSRFCheck middleware loaded")
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)