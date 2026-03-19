from django.shortcuts import render
from .forms import UserForm

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


def signup(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user_form.save()
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(
        request,
        'rate_the_view/signup.html',
        {'user_form': user_form, 'registered': registered}
    )