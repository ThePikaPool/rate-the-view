from django.shortcuts import render

def home(request):

    # Example placeholder data for homepage posts
    # This is temporary so the template can render
    # Teammate who implements the database should replace this
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