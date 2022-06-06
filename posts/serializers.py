from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from posts.models import (
    Post,
    Attachment, Profile)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('user',
                  'tg_info')


class ProfileCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'


class AttachmentInPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = ('image', )


class AttachmentLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = ('id', )


class AttachmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('name',
                  'text',
                  'is_draft',
                  'tg_post',
                  'vk_post')


class PostSerializer(serializers.ModelSerializer):
    attachments = AttachmentInPostSerializer(many=True)
    # author = BloggerSerializer()

    class Meta:
        model = Post
        fields = ('id',
                  'name',
                  'text',
                  'author',
                  'is_draft',
                  'date_created',
                  'tg_post',
                  'vk_post',
                  'attachments'
                  )


class DraftToPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('is_draft', )


class VKAuthenticationLinkSerializer(serializers.Serializer):
    link = serializers.URLField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "id")
