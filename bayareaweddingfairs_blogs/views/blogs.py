from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from bayareaweddingfairs_blogs.models import PostModel, CommentModel
from bayareaweddingfairs_blogs.forms.CommentForm import CommentFormAdd
from django.utils import timezone
from bayareaweddingfairs_blogs.forms.PostsForms import *
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# Create your views here.


def post_list(request):
    posts = PostModel.objects.filter(published_date__lte = timezone.now()).order_by('published_date')[:5]
    recentPosts = PostModel.objects.all().order_by('-created_date')[:5]
    post_comments = None
    for p in posts:
        post_comments = CommentModel.objects.filter(comment_post=p)
    return render(request, 'blogs/post_list.html', {'posts':posts, 'post_comments':post_comments, 'recentPosts': recentPosts})


def post_new(request):
    form = PostCreateForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        print "image: ", form.cleaned_data['img']
        post.author = request.user
        post.published_date = timezone.now()

        post.save()
        return redirect('post_list')
    else:
        form = PostCreateForm()
    return render(request, 'blogs/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(PostModel, pk=pk)
    if request.method == "POST":
        form = PostCreateForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostCreateForm(instance=post)
    return render(request, 'blogs/post_edit.html', {'form': form})


def user_post(request):
    posts = PostModel.objects.filter(author=request.user)
    return render(request, 'blogs/user_post.html',{'posts':posts})


def post_delete(request, pk):
    post = get_object_or_404(PostModel, pk=pk)
    del_query = PostModel.objects.filter(pk=pk).delete()
    print del_query
    return HttpResponseRedirect(reverse("user_post"))


def post_detail(request, pk):
    post = get_object_or_404(PostModel, pk = pk)
    post_comments = CommentModel.objects.filter(comment_post=post)
    if request.method == 'POST':
        form = CommentFormAdd(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.comment_post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
        else:
            form = CommentFormAdd()
    else:
        form = CommentFormAdd()

    return render(request, 'blogs/post_detail.html', {'post':post, 'form':form, 'post_comments':post_comments })


def add_comment(request, pk):
    """Add a comment to POST
        
    :param request: 
    :param pk: post ID
    :return: 
    """
    post = get_object_or_404(PostModel, pk=pk)
    if request.method == 'POST':
        form = CommentFormAdd(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.comment_post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
        else:
            form = CommentFormAdd()
    else:
        form = CommentFormAdd()

    return render(request, "blogs/post_detail.html",{'form': form, 'pk': pk})
