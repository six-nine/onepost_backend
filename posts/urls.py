from django.urls import path
from posts.views import (PostsList,
                         PostDetail,
                         PostCreate,
                         AttachmentsList,
                         AttachmentCreate)


urlpatterns = [
    path('posts/', PostsList.as_view()),
    path('posts/<int:pk>/', PostDetail.as_view()),
    path('posts/create/', PostCreate.as_view()),
    path('attachments/', AttachmentsList.as_view()),
    path('attachments/create/', AttachmentCreate.as_view())
]
