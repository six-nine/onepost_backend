from django.db import models
from django.contrib.auth.models import User


class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class VKAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)



class TelegramAccount(models.Model):
    pass


class Post(models.Model):
    name = models.CharField(max_length=50, null=True)
    text = models.TextField(max_length=2000)
    author = models.ForeignKey(Blogger, default=None, null=True, on_delete=models.CASCADE)
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
