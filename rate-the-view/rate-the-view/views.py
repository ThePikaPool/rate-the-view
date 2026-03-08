from django.shortcuts import render

def home(request):
    context_dict = {}
    return render(request, 'rate-the-veiw/home.html', context=context_dict)