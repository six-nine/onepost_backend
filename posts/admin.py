from django.contrib import admin
from .models import Profile, Post, Attachment, TelegramInfo, VKInfo


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Attachment)
admin.site.register(TelegramInfo)
admin.site.register(VKInfo)
