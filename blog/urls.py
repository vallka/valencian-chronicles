from django.urls import path

from .views import *

app_name = 'blog'

urlpatterns = [
    path('', ListView.as_view(), name='list'),
    path('search/', SearchView.as_view(), name='search'),
    path('<str:slug>/', PostView.as_view(), name='post'),
    path('category/<str:slug>/', ListView.as_view(), name='post-by-cat'),
]
