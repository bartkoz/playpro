from django.contrib import admin

from users.models import User, UserAvatar, School

admin.site.register(User)
admin.site.register(UserAvatar)
admin.site.register(School)
