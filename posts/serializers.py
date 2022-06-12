from rest_framework import serializers
from django.contrib.auth.models import User
from posts.models import (
    Post,
    Attachment,
    Profile,
    TelegramInfo,
    VKInfo)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email']


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
    attachments = serializers.ListSerializer(child=AttachmentCreateSerializer())

    def create(self, validated_data):
        attachments = validated_data.pop('attachments')
        attachments_instances = []
        for attachment in attachments:
            instance = Attachment.objects.create(**attachment)
            attachments_instances.append(instance)
        post_instance = Post.objects.create(**validated_data)
        post_instance.attachments.set(attachments_instances)
        return post_instance

    class Meta:
        model = Post
        fields = ('id',
                  'name',
                  'text',
                  'tg_post',
                  'vk_post',
                  'attachments')


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('name',
                  'text',
                  'tg_post')


class PostSerializer(serializers.ModelSerializer):
    attachments = AttachmentInPostSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id',
                  'name',
                  'text',
                  'author',
                  'date_created',
                  'tg_post',
                  'attachments'
                  )


class PostMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id',
                  'name',
                  'date_created')


class VKAuthenticationLinkSerializer(serializers.Serializer):
    link = serializers.URLField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'id')


class TelegramInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramInfo
        fields = ('chat_id', )


class VKInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VKInfo
        fields = ('access_token', )


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    vk_info = VKInfoSerializer()
    tg_info = TelegramInfoSerializer()

    class Meta:
        model = Profile
        fields = ('user',
                  'tg_info',
                  'vk_info')
