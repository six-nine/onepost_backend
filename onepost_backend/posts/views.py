from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from posts.serializers import (PostSerializer,
                               PostCreateSerializer,
                               PostUpdateSerializer,
                               PostMinimalSerializer,
                               AttachmentSerializer,
                               AttachmentCreateSerializer,
                               ProfileSerializer,
                               VKAuthenticationLinkSerializer,
                               RegisterSerializer, TelegramInfoSerializer)
from .models import (Post, Attachment, Profile, VKInfo, TelegramInfo)
from django.conf import settings
from .tasks import send_post_tg, delete_post_tg, edit_post_tg, send_message_vk
from .utils import vk_get_access_code
from django.shortcuts import get_object_or_404


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

        if post.tg_post and hasattr(user, 'tg_info'):
            send_post_tg.delay(post.pk)

        if post.vk_post and hasattr(user, 'vk_info'):
            send_message_vk.delay(post.pk)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PostUpdateSerializer
        else:
            return PostSerializer

    def perform_destroy(self, instance):
        if instance.tg_post:
            delete_post_tg.delay(instance.tg_message_chat_id,
                                instance.tg_message_id)
        instance.delete()

    def perform_update(self, serializer):
        changed_post = serializer.save()

        if changed_post.tg_post:
            edit_post_tg.delay(changed_post.tg_message_chat_id,
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

    def get(self, request):
        user = self.request.user
        profile = user.profile

        serializer = ProfileSerializer(profile)

        return Response(serializer.data)


class VKAuthGetCode(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        token = vk_get_access_code(request.GET.get("code"))
        id = request.GET.get("id")
        profile = get_object_or_404(Profile, pk=id)
        if token:
            info, created = VKInfo.objects.get_or_create(profile=profile)
            info.access_token = token
            info.save()

        return Response()


class VKGetAuthLink(APIView):

    def post(self, request, *args, **kwargs):
        if "group_id" in request.data:
            link = settings.VK_AUTHENTICATION_BASE_URL + "?";
            group_id = request.data["group_id"]
            params = {
                "client_id": settings.VK_APP_ID,
                "redirect_uri": settings.VK_REDIRECT_URL +
                                "?id=" + str(request.user.profile.pk),
                "group_ids": str(group_id),
                "display": "page",
                "scope": "messages",
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
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.data
        serializer = RegisterSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TelegramInfoCreateUpdate(APIView):
    def post(self, request):

        serializer = TelegramInfoSerializer(data=request.data)
        serializer.is_valid()
        validated_data = serializer.validated_data

        if 'chat_id' not in validated_data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        info, created = TelegramInfo.objects.get_or_create(
            profile=request.user.profile)
        info.chat_id = validated_data.get('chat_id')
        info.save()

        return Response(status=status.HTTP_201_CREATED)
