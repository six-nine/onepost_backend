from django.urls import path
from posts.views import (PostsList,
                         PostDetail,
                         PostCreate,
                         AttachmentsList,
                         AttachmentCreate,
                         DraftsList,
                         DraftToPost,
                         ProfileDetail)


urlpatterns = [
    path('posts/', PostsList.as_view()),
    path('posts/<int:pk>/', PostDetail.as_view()),
    path('posts/<int:pk>/send/', DraftToPost.as_view()),
    path('posts/create/', PostCreate.as_view()),

    path('posts/drafts/', DraftsList.as_view()),

    path('attachments/', AttachmentsList.as_view()),
    path('attachments/create/', AttachmentCreate.as_view()),

    path('profile/', ProfileDetail.as_view())
]
