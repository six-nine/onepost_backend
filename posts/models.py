from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name="profile")
    telegram_chat_id = models.IntegerField(null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class VKAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class TelegramAccount(models.Model):
    pass


class Post(models.Model):
    name = models.CharField(max_length=50, null=True)
    text = models.TextField(max_length=2000)
    author = models.ForeignKey(Profile, default=None, null=True, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)
    tg_post = models.BooleanField(default=True)
    vk_post = models.BooleanField(default=True)


class Attachment(models.Model):
    image = models.ImageField(upload_to='posts_images/')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=True,
                             related_name="attachments")
