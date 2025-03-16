from django.contrib import admin
from django.contrib.auth.models import User
from .models import RegisterModel

class RegisterModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'address', 'is_active', 'is_verified', 'created_at', 'updated_at')
    search_fields = ('username', 'email', 'phone_number')

admin.site.register(RegisterModel, RegisterModelAdmin)
admin.site.unregister(User)
admin.site.register(User)