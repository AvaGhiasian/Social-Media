from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import *
from .models import *


# Create your views here.

def log_out(request):
    logout(request)
    return HttpResponse("شما خارج شدید.")


def profile(request):
    user = User.objects.prefetch_related('followers').get(id=request.user.id)
    saved_posts = user.saved_posts.all()
    my_posts = user.user_posts.all()[:8]
    return render(request, 'social/profile.html', {'saved_posts': saved_posts, 'my_posts': my_posts})


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
        return redirect('social:profile')
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
    posts = Post.objects.select_related('author').all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
        page = request.GET.get('page')
        paginator = Paginator(posts, 5)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            post = paginator.page(1)
        except EmptyPage:
            posts = []

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "social/list_ajax.html", {'posts': posts})

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
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:5]
    context = {
        'post': post,
        'similar_posts': similar_posts,
    }
    return render(request, "social/detail.html", context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')  # this post_id comes from template
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        like_count = post.likes.count()
        response_data = {
            'liked': liked,
            'like_count': like_count,
        }
    else:
        response_data = {
            'error': 'invalid post_id'
        }

    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True

        return JsonResponse({'saved': saved})
    return JsonResponse({'error': 'invalid request'})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User,username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()

            return JsonResponse({'follow': follow, 'following_count': following_count,
                                 'followers_count': followers_count})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist.'})

    return JsonResponse({'error': 'Invalid request.'})

