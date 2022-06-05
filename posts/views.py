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
                               UserSerializer)
from django.core.exceptions import ObjectDoesNotExist
from .models import (Post, Attachment, Profile)
from .social_networks_apis import tg


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
