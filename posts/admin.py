from django.contrib import admin
from .models import Blogger, Post, Attachment, Admin


admin.site.register(Blogger)
admin.site.register(Post)
admin.site.register(Attachment)
admin.site.register(Admin)
