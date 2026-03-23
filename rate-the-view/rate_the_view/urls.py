from django.urls import path
from . import views

app_name = 'rate_the_view'

urlpatterns = [
    # Home/main
    path('', views.home, name= 'home'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User profile
    path('user/<str:username>/', views.profile, name='profile'),

    # Static
    path('contact-us/', views.contact_us, name='contact_us'),

    # Post detail
    path('posts/<slug:slug>/', views.view_post_detail, name='view_post_detail'),

    # Voting
    path('posts/<slug:slug>/upvote/', views.upvote_post, name='upvote'),
    path('posts/<slug:slug>/downvote/', views.downvote_post, name='downvote'),
    
]
