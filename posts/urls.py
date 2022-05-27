from django.urls import path
from posts.views import (PostsList, AttachmentsList)


urlpatterns = [
    path('', PostsList.as_view()),
    path('attachments/', AttachmentsList.as_view())
]
