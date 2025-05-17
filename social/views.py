from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from taggit.models import Tag
from django.db.models import Count

from .forms import *
from .models import *


# Create your views here.

def log_out(request):
    logout(request)
    return HttpResponse("شما خارج شدید.")


def profile(request):
    return HttpResponse("You're at the profile page.")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_user(request):
    if request.method == 'POST':
        form = UserEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'registration/edit_user.html', {'form': form})


def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = data['subject']
            message = f"{data['name']}\n{data['email']}\n{data['phone']}\n\n{data['message']}"
            from_email = 'avaghiasian82@gmail.com'
            to_email = ['avaghiasian03@gmail.com']
            send_mail(subject, message, from_email, to_email, fail_silently=False)
            messages.success(request, 'پیام شما با موفقیت ارسال شد.')
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


def post_list(request, tag_slug=None):
    posts = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    context = {
        'posts': posts,
        'tag': tag,
    }
    return render(request, "social/list.html", context)


def create_post(request):
    if request.method == 'POST':
        form = CreatePostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('social:posts')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create-post.html', {'form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=pk)
    similar_posts= similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:5]
    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, "social/detail.html", context)