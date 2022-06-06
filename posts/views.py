from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from posts.serializers import (PostSerializer,
                               PostCreateSerializer,
                               AttachmentSerializer,
                               AttachmentCreateSerializer,
                               DraftToPostSerializer,
                               ProfileSerializer,
                               UserSerializer,
                               VKAuthenticationLinkSerializer,
                               RegisterSerializer)
from django.core.exceptions import ObjectDoesNotExist
from .models import (Post, Attachment, Profile, VKInfo)
from .social_networks_apis import tg, vk
from django.conf import settings

# TODO: permissions

class PostsList(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostCreate(generics.CreateAPIView):
    serializer_class = PostCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        created_post = serializer.instance

        if "attachments" in request.data:
            for attachment_id in request.data["attachments"]:
                try:
                    attachment = Attachment.objects.get(id=attachment_id)
                    attachment.post = created_post
                    attachment.save()
                except ObjectDoesNotExist:
                    pass

        if not created_post.is_draft:
            try:
                if created_post.tg_post:
                    tg.send_post(created_post)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        created_post.author = request.user.profile
        created_post.save()

        return Response(status=status.HTTP_201_CREATED)


class PostDetail(generics.RetrieveUpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostsPostedList(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_draft=False)


class DraftsList(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_draft=True)


class DraftToPost(generics.UpdateAPIView):
    serializer_class = DraftToPostSerializer
    queryset = Post.objects.all()

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        was_draft = post.is_draft
        draft = request.data.get('is_draft')
        if draft or not was_draft:
            return super().update(request, *args, **kwargs)
        else:
            tg.send_post(post)
            return super().update(request, *args, **kwargs)


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
