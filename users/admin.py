from django.contrib import admin

from users.models import User, UserAvatar

admin.site.register(User)
admin.site.register(UserAvatar)
