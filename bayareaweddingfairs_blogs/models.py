from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.db.models import permalink
from django.template.defaultfilters import slugify

# Create your models here.


class PostModel(models.Model):
    """Posts of a blogs"""
    author = models.ForeignKey('auth.User')
    # category_id = models.ForeignKey('CategoryModel')
    title = models.CharField(max_length=100, blank=False)
    post_slug = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    img = models.ImageField(db_index=True, upload_to="blogs/images", null=True, blank=True)

    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    @permalink
    def get_absolute_url(self):
        return ('view_blog_post', None, { 'post_slug': self.post_slug })

    def __str__(self):
       return self.title

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        postSlug = PostModel.objects.filter(post_slug__exact=slug)
        if postSlug.count() > 0:
            super(PostModel, self).save(*args, **kwargs)
            self.post_slug = slug+'-'+ str(self.id)
            super(PostModel, self).save(*args, **kwargs)

        else:
            self.post_slug = slug
            super(PostModel, self).save(*args, **kwargs)


class CategoryModel(models.Model):
    """Category of POST"""
    category_title = models.CharField(max_length=100, db_index=True)
    category_slug = models.CharField(max_length=100, db_index=True)

    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s' % self.category_title

    @permalink
    def get_absolute_url(self):
        return ('view_blog_category', None, { 'category_slug': self.category_slug })


class CommentModel(models.Model):
    """Comment of the POST """
    comment_author = models.ForeignKey('auth.User', related_name='comment_author', null=True, blank=True)   #null and blank is used for the anonymous user
    comment_post = models.ForeignKey('PostModel', related_name='commented_post')      #related name to differentiate the attribute from  other
    text = models.CharField(max_length=120)
    created_date = models.DateTimeField(default=timezone.now)

