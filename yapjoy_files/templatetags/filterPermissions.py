from django import template
from django.utils.encoding import force_unicode
from yapjoy_files.models import UserPermissionPage
import re
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def get_user_permissions(req, args):
    user = User.objects.get(pk=req.user.id)
    permission = UserPermissionPage.objects.filter(user=user, crmUrl__url_path__icontains=args,
                                                   user_allowed=True)
    if user.is_superuser:
        return True
    elif permission:
        return True

    else:
        return False