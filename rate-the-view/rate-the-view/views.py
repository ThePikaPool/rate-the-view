from django.shortcuts import render

def home(request):
    return render(request, 'rate-the-view/home.html')