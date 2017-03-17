from django.contrib.auth.models import User
def get_or_create_user(email):
    user = None
    try:
        user = User.objects.get(email__iexact=email)
    except:
        user = User.objects.create(email=email, username=email)
    return user
