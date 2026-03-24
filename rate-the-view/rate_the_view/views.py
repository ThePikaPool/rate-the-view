from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Follow
from . import services
import random


def home(request):
    all_posts = Post.objects.select_related('created_by').all()
    top_views = Post.objects.all()[:3]

    followed_user_ids = []
    if request.user.is_authenticated:
        # gets a list of all the ids of people who the user follows

        followed_user_ids = list(
            services.get_followed_by(request.user).values_list('following_id', flat=True)
        )
        # changed the above to use services.py instead of its own thing, this'll
        # make the code cleaner - David

        # alg for homepage begins here

        number_of_followed_users = len(followed_user_ids)
        random_indices = [random.randint(0, number_of_followed_users-1) for i in range(5)]
        # this picks random people from the list that the user follows

        randomly_chosen_followed_ids = [followed_user_ids[x] for x in random_indices]
        corresponding_users = [User.objects.filter(id=x) for x in randomly_chosen_followed_ids]
        # this uses the previous rng to get the ids and therefore user objects from the database

        followed_posts_complex = [Post.objects.filter(created_by=x) for x in corresponding_users]
        flattened_posts = services.unravel_list(followed_posts_complex)
        # then, get all the posts these users have made and flatten out the list

        posts = flattened_posts.extend(top_views)
        #put the posts in a list with the top views...
        random.shuffle(posts)
        # and shuffle it around randomly :)

        # all - David

    else:
        posts = top_views
        
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

def upload(request):
    return render(request, 'rate_the_view/upload.html')

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