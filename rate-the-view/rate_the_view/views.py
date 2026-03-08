from django.shortcuts import render

def home(request):
    return render(request, 'rate_the_view/home.html')