from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import (
    Post,
    Blogger,
    Attachment)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class BloggerSerializer(serializers.ModelSerializer):
    user = UserSerializer

    class Meta:
        model = Blogger
        fields = '__all__'


class BloggerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blogger
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # attachments = AttachmentSerializer(many=True)
    # author = BloggerSerializer()

    class Meta:
        model = Post
        fields = ('name',
                  'text',
                  'author',
                  'is_draft',
                  'date_created',
                  'tg_post',
                  'vk_post',
                  'ok_post',
                  'attachments'
                  )
