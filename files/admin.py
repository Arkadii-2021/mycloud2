from django.contrib import admin
from .models import File, Folder


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['label', 'file']


@admin.register(Folder)
class FileAdmin(admin.ModelAdmin):
    list_display = ['label']
