from django.urls import path
from posts.views import (PostsList,
                         PostDetail,
                         PostCreate,
                         AttachmentsList,
                         AttachmentCreate,
                         ProfileDetail,
                         VKAuthGetCode,
                         VKGetAuthLink,
                         Register,
                         TelegramInfoCreateUpdate)


urlpatterns = [
    path('posts/', PostsList.as_view(), name="my_posts"),
    path('posts/<int:pk>/', PostDetail.as_view(), name="post_detail"),
    path('posts/create/', PostCreate.as_view(), name="post_creation"),

    path('attachments/', AttachmentsList.as_view()),
    path('attachments/create/', AttachmentCreate.as_view()),

    path('profile/', ProfileDetail.as_view(), name="profile"),

    path('social_networks/add/vk/auth_code/', VKAuthGetCode.as_view()),
    path('social_networks/add/vk/get_link/', VKGetAuthLink.as_view(),
         name="vk_get_link"),

    path('social_networks/add/tg/', TelegramInfoCreateUpdate.as_view()),

    path('register/', Register.as_view(), name="register")
]
