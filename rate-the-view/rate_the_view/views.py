from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):

    #Example placeholder data for homepage posts
    #This is temporary so the template can render
    #Teammate who implements the database should replace this
    posts = [
        {
            "username": "callum3925",
            "location": "Isle of Skye",
            "title": "Sunset at Isle of Skye",
            "votes": 82
        }
    ]

    context = {"posts": posts}

    return render(request, 'rate_the_view/home.html', context)

@login_required
def profile(request, username):

    #Example placeholder data for homepage posts
    #This is temporary so the template can render
    #Teammate who implements the database should replace this
    user = {
        "username": username,
        "bio": "Travel photographer exploring scenic views around the world.",
        "total_likes": 421,
        "total_posts": 4,
        "following": 82,
        "followers": 2211
    }

    #Example placeholder posts belonging to the user
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

    context = {
        "user": user,
        "posts": posts
    }

    return render(request, 'rate_the_view/profile.html', context)


def contact_us(request):
    return render(request, 'rate_the_view/contact_us.html')

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