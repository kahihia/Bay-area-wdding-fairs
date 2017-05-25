from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.template import *
from yapjoy_files.models import *
import re


def is_permitted(function):
    """decorator for sidebar permission
    
    :param function: 
    :return: Permission error/ function
    """
    def wrap(request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        print "req: ", request.path
        urlpath = request.path
        if hasNumbers(urlpath):
            urlpath = splitInt(urlpath)
        permission = UserPermissionPage.objects.filter(user=user, crmUrl__url_path__icontains=urlpath, user_allowed=True)

        if user.is_superuser:
            return function(request, *args, **kwargs)
        elif permission:
            return function(request, *args, **kwargs)

        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def hasNumbers(inputString):
    """Check the URL int at the end 
    
    :param inputString: 
    :return: True/False
    """
    return bool(re.search(r'\d', inputString))


def splitInt(inputstring):
    """ split the integer from url
    
    :param inputstring: 
    :return: string url 
    """
    n = re.findall('\d+', inputstring)
    return inputstring.split(n[0])[0]

