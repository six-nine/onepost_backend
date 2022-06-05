from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from posts.serializers import (PostSerializer,
                               PostCreateSerializer,
                               AttachmentSerializer,
                               AttachmentCreateSerializer,
                               DraftToPostSerializer,
                               ProfileSerializer,
                               UserSerializer,
                               VKAuthenticationLinkSerializer)
from django.core.exceptions import ObjectDoesNotExist
from .models import (Post, Attachment, Profile)
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
            tg.send_post(created_post)

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
        print(request)
        print(args)
        print(kwargs)
        print(request.user.is_authenticated)
        print(request.user.pk)

        print(request.GET)
        vk.get_access_code(request.GET.get("code"))

        return Response()

class VKGetAuthLink(APIView):

    def post(self, request, *args, **kwargs):
        print(request.data)
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
