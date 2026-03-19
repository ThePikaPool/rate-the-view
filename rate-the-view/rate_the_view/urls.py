from django.urls import path
from . import views

app_name = 'rate_the_view'

urlpatterns = [
    path('', views.home, name= 'home'),
    path('user/<str:username>/', views.profile, name='profile'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('signup/', views.signup, name='signup'),
]