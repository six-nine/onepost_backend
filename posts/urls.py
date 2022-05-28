from django.urls import path
from posts.views import (PostsList, PostDetail, AttachmentsList)


urlpatterns = [
    path('posts/', PostsList.as_view()),
    path('posts/<int:pk>/', PostDetail.as_view()),
    path('attachments/', AttachmentsList.as_view())
]
