from rest_framework import generics
from posts.serializers import (PostSerializer, AttachmentSerializer)
from .models import (Post, Attachment)


class PostsList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostDetail(generics.RetrieveAPIView):
    serializer_class = PostSerializer


class AttachmentDetail(generics.RetrieveAPIView):
    serializer_class = AttachmentSerializer


class AttachmentsList(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    queryset = Attachment.objects.all()
