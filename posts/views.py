from rest_framework import generics
from posts.serializers import PostSerializer
from .models import Post


class PostsList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class PostDetail(generics.RetrieveAPIView):
    serializer_class = PostSerializer
