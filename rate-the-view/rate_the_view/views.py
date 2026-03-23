from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Follow


def home(request):
    posts = Post.objects.select_related('created_by').all()
    top_views = Post.objects.all()[:3]

    followed_user_ids = []
    if request.user.is_authenticated:
        followed_user_ids = list(
            Follow.objects.filter(follower=request.user)
            .values_list('following_id', flat=True)
        )

    context = {
        "posts": posts,
        "top_views": top_views,
        "followed_user_ids": followed_user_ids,
    }

    return render(request, 'rate_the_view/home.html', context)


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Example placeholder posts belonging to the user
    posts = [
        {
            "image": "https://via.placeholder.com/300",
            "votes": 120
        },
        {
            "image": "https://via.placeholder.com/300",
            "votes": 98
        },
        {
            "image": "https://via.placeholder.com/300",
            "votes": 162
        }
    ]

    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    context = {
        "profile_user": profile_user,
        "posts": posts,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
    }

    return render(request, 'rate_the_view/profile.html', context)


def contact_us(request):
    return render(request, 'rate_the_view/contact_us.html')

def signup(request):
    return render(request, 'rate_the_view/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('rate_the_view:home')
        else:
            context = {"error": "Invalid username or password"}
            return render(request, 'rate_the_view/login.html', context)

    return render(request, 'rate_the_view/login.html')


def logout_view(request):
    logout(request)
    return redirect('rate_the_view:home')


def view_post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    context = {
        'post': post,
    }
    return render(request, 'rate_the_view/view_post.html', context)


@login_required
def upvote_post(request, slug):
    if request.method == "POST":
        post = get_object_or_404(Post, slug=slug)

        post.downvotes.remove(request.user)

        if post.upvotes.filter(id=request.user.id).exists():
            post.upvotes.remove(request.user)
        else:
            post.upvotes.add(request.user)

    return redirect('rate_the_view:home')


@login_required
def downvote_post(request, slug):
    if request.method == "POST":
        post = get_object_or_404(Post, slug=slug)

        post.upvotes.remove(request.user)

        if post.downvotes.filter(id=request.user.id).exists():
            post.downvotes.remove(request.user)
        else:
            post.downvotes.add(request.user)

    return redirect('rate_the_view:home')


@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    # Prevent users from following themselves
    if request.user == target_user:
        return redirect('rate_the_view:profile', username=username)

    existing_follow = Follow.objects.filter(
        follower=request.user,
        following=target_user
    ).first()

    if existing_follow:
        existing_follow.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=target_user
        )

    return redirect(request.META.get('HTTP_REFERER', 'rate_the_view:home'))