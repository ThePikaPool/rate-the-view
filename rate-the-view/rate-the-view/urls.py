from django.urls import path
from . import views

app_name = 'rate_the_view'

urlpatterns = [
    path('', views.home, name= 'home'),
]