from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posts.serializers import (PostSerializer,
                               PostCreateSerializer,
                               PostUpdateSerializer,
                               PostMinimalSerializer,
                               AttachmentSerializer,
                               AttachmentCreateSerializer,
                               ProfileSerializer,
                               UserSerializer,
                               VKAuthenticationLinkSerializer,
                               RegisterSerializer, TelegramInfoSerializer)
from .models import (Post, Attachment, Profile, VKInfo, TelegramInfo)
from django.conf import settings
from .tasks import send_post, delete_post, edit_post
from .social_networks_apis import vk


class PostsList(generics.ListAPIView):
    serializer_class = PostMinimalSerializer

    def get_queryset(self):
        user = self.request.user.profile
        return Post.objects.filter(author=user)


class PostCreate(generics.CreateAPIView):
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        post = serializer.save()
        user = self.request.user.profile
        post.author = user
        post.save()

        send_post.delay(post.pk)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'UPDATE'):
            return PostUpdateSerializer
        else:
            return PostSerializer

    def perform_destroy(self, instance):
        delete_post.delay(instance.tg_message_chat_id, instance.tg_message_id)
        instance.delete()

    def perform_update(self, serializer):
        changed_post = serializer.save()
        edit_post.delay(changed_post.tg_message_chat_id,
                        changed_post.tg_message_id,
                        changed_post.text)


class AttachmentDetail(generics.RetrieveAPIView):
    serializer_class = AttachmentSerializer


class AttachmentCreate(generics.CreateAPIView):
    serializer_class = AttachmentCreateSerializer


class AttachmentsList(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()


class ProfileDetail(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = self.request.user
        profile = user.profile

        serializer = ProfileSerializer(profile)

        return Response(serializer.data)


class VKAuthGetCode(APIView):

    def get(self, request, *args, **kwargs):
        token = vk.get_access_code(request.GET.get("code"))
        if token:
            try:
                request.user.profile.vk_info.access_token = token
                request.user.profile.vk_info.save()
            except Profile.vk_info.RelatedObjectDoesNotExist:
                new_info = VKInfo(profile=request.user.profile,
                                  access_token=token)
                new_info.save()

        return Response()

class VKGetAuthLink(APIView):

    def post(self, request, *args, **kwargs):
        if "group_id" in request.data:
            link = settings.VK_AUTHENTICATION_BASE_URL + "?";
            group_id = request.data["group_id"]
            params = {
                "client_id": settings.VK_APP_ID,
                "redirect_uri": settings.VK_REDIRECT_URL,
                "group_ids": str(group_id),
                "display": "page",
                "scope": "wall",
                "response_type": "code",
                "v": "5.131"
            }

            for key, value in params.items():
                link += key + "=" + value + "&"

            link = link[:-1]
            data = {"link": link}
            serializer = VKAuthenticationLinkSerializer(data=data)

            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Register(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = RegisterSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TelegramInfoCreateUpdate(APIView):
    def post(self, request):
        has_tg = hasattr(request.user.profile, "tg_info")
        info = None
        if has_tg:
            info = request.user.profile.tg_info
        else:
            info = TelegramInfo(profile=request.user.profile, chat_id=0)
        serializer = TelegramInfoSerializer(data=request.data)
        if serializer.is_valid():
            if "chat_id" in serializer.validated_data:
                info.chat_id = serializer.validated_data["chat_id"]
                info.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


