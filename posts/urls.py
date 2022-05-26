from django.urls import path
from posts.views import PostsList


urlpatterns = [
    path('', PostsList.as_view())
]
