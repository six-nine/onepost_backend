from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from posts.serializers import (PostSerializer,
                               PostCreateSerializer,
                               AttachmentSerializer,
                               AttachmentCreateSerializer)
from django.core.exceptions import ObjectDoesNotExist
from .models import (Post, Attachment)
from .social_networks_apis import tg


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

        if not serializer.instance.is_draft:
            tg.send_post(serializer.instance)

        return Response(serializer.validated_data,
                        status=status.HTTP_201_CREATED)


class PostDetail(generics.RetrieveUpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class DraftsList(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(is_draft=True)


class AttachmentDetail(generics.RetrieveAPIView):
    serializer_class = AttachmentSerializer


class AttachmentCreate(generics.CreateAPIView):
    serializer_class = AttachmentCreateSerializer


class AttachmentsList(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
