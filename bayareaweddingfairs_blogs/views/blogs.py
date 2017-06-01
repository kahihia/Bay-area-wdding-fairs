from django.shortcuts import render
from bayareaweddingfairs_blogs.models import PostModel, CommentModel
from django.utils import timezone
# Create your views here.


def post_list(request):
    posts = PostModel.objects.filter(published_date__lte = timezone.now()).order_by('published_date')
    # print "posts: ", posts
    post_comments = None
    for p in posts:
        post_comments = CommentModel.objects.filter(comment_post=p)
        # print "post_comment: ", post_comments
    # post_comments = Comment()
    return render(request, 'blog/post_list.html',{'posts':posts, 'post_comments':post_comments  })
