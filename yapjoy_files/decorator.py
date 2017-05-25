from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.template import *
from yapjoy_files.models import *


def is_permitted(function):
    """decorator for sidebar permission
    
    :param function: 
    :return: 
    """
    def wrap(request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        permission = UserPermissionPage.objects.filter(user=user, crmUrl__url_path__icontains=request.get_full_path, user_allowed=True)

        if user.is_superuser:
            return function(request, *args, **kwargs)
        elif permission:
            return function(request, *args, **kwargs)

        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap