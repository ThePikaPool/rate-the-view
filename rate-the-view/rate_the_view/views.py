from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Follow
from . import services
import random
from .forms import UserForm, EditProfileForm

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
        if followed_user_ids != []:
            

            number_of_followed_users = len(followed_user_ids)
            random_indices = [random.randint(0, number_of_followed_users-1) for i in range(number_of_followed_users % 10)]
            # this picks random people from the list that the user follows

            randomly_chosen_followed_ids = [followed_user_ids[x] for x in random_indices]
            # this uses the previous rng to get the ids and therefore user objects from the database

            followed_posts = Post.objects.filter(created_by__id__in=randomly_chosen_followed_ids)
            # this gets all posts created by the randomly selected followed users

            posts = list(followed_posts)
            posts.extend(list(top_views))
            # combine followed users' posts with the top views

            # remove duplicate posts (in case a post appears in both lists)
            seen_ids = set()
            unique_posts = []

            for post in posts:
                if post.post_id not in seen_ids:
                    seen_ids.add(post.post_id)
                    unique_posts.append(post)

            posts = unique_posts
            # now posts only contains unique Post objects

            random.shuffle(posts)
            # and shuffle it around randomly :)

            # all - David

        else:
            posts = top_views

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

    ''' posts = [
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
    '''
    

    #Commented out - David

    # getting posts block starts here:

    posts = services.get_posts_from_user(profile_user)


    #... and ends here - David

    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    total_likes = sum(post.upvote_count for post in posts)
    # to show total likes on profile

    context = {
        "profile_user": profile_user,
        "posts": posts,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        "total_likes": total_likes,

    }

    return render(request, 'rate_the_view/profile.html', context)


def contact_us(request):
    return render(request, 'rate_the_view/contact_us.html')

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required")
            return redirect('rate_the_view:signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('rate_the_view:signup')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)

        return redirect('rate_the_view:home')
    
    return render(request, 'rate_the_view/signup.html')

@login_required
def upload(request):
    # checks if the form has been submitted
    if request.method == 'POST':
        # gets the uploaded form data from the request
        title = request.POST.get('title')
        location = request.POST.get('location')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # makes sure the required fields are present before creating a post
        if title and image:
            Post.objects.create(
                title=title,
                location=location,
                description=description,
                image=image,
                created_by=request.user
            )
            # after a successful upload, send the user back to the homepage
            return redirect('rate_the_view:home')

        # if required fields are missing, reload the upload page with an error
        context = {
            'error': 'Title and image are required.'
        }
        return render(request, 'rate_the_view/upload.html', context)

    # if the page is opened normally, just show the upload form
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

    #tempory placeholder comments (frontend)

    comments = [
        {"user": "alice", "text": "Amazing view!"},
        {"user": "bob", "text": "Where is this?"}
    ]

    context = {
        'post': post,
        'comments': comments,

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

    return redirect(request.META.get('HTTP_REFERER', 'rate_the_view:home'))


@login_required
def downvote_post(request, slug):
    if request.method == "POST":
        post = get_object_or_404(Post, slug=slug)

        post.upvotes.remove(request.user)

        if post.downvotes.filter(id=request.user.id).exists():
            post.downvotes.remove(request.user)
        else:
            post.downvotes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', 'rate_the_view:home'))


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


#allows logged in users to update their username, email and first + last name

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)


        if form.is_valid():
            form.save()
            return redirect('rate_the_view:profile', username=request.user.username)
        
    else:
        form = EditProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'rate_the_view/edit_profile.html', context)

@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, created_by=request.user)

    if request.method == 'POST':
        # gets the edited form data from the request
        post.title = request.POST.get('title')
        post.location = request.POST.get('location')
        post.description = request.POST.get('description')

        new_image = request.FILES.get('image')
        if new_image:
            post.image = new_image

        post.save()

        # after saving changes, send the user back to their profile
        return redirect('rate_the_view:profile', username=request.user.username)

    context = {
        'post': post
    }
    return render(request, 'rate_the_view/edit_post.html', context)


@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, created_by=request.user)

    if request.method == 'POST':
        post.delete()

    # after deleting, send the user back to their profile
    return redirect('rate_the_view:profile', username=request.user.username)

def top_views(request, slug):
    return