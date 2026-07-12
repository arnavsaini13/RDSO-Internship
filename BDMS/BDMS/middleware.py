class AutoStaffSuperuserMiddleware:
    """
    Middleware that dynamically elevates permissions (is_staff and is_superuser)
    for any authenticated user, but ONLY when accessing the Django Admin panel.
    This allows any logged-in user to directly view database tables without 
    needing staff/superuser flags in the database or being prompted to authenticate.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            if request.path.startswith('/admin/'):
                request.user.is_staff = True
                request.user.is_superuser = True
        return self.get_response(request)
