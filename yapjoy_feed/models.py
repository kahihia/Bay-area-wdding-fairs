from django.db import models
from django.contrib.auth.models import User
from yapjoy import settings
class Post(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, related_name="post_user")
    user_wall = models.ForeignKey(User, related_name='post_user_wall')

    image = models.ImageField(upload_to='media/', null=True, blank=True)

    likers = models.ManyToManyField(User, through='PostLike', related_name='userlikes', null=True, blank=True)
    comments = models.ManyToManyField(User, through='PostComments', related_name='userComments', null=True, blank=True)
    favourites = models.ManyToManyField(User, related_name='userfavourites', null=True, blank=True)

    likes_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_image_url(self):
        return "%s%s"%(settings.MEDIA_URL, self.image)


class PostLike(models.Model):
    user = models.ForeignKey(User)
    statuspost = models.ForeignKey(Post)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class PostComments(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    comment = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class pictureWall(models.Model):
    user = models.ForeignKey(User)
    picture = models.ImageField(upload_to='media/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_image_url(self):
        return "%s%s"%(settings.MEDIA_URL, self.picture)