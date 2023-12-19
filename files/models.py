from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
import os
from django.conf import settings

user = get_user_model()


def file_path(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    return 'files/storages/{userid}/{basename}{ext}'.format(
        userid=instance.user.id,
        basename=basefilename,
        ext=file_extension)


class Folder(MPTTModel):
    """MPT-Модель папок"""
    label = models.CharField('Название', max_length=100)
    date = models.DateTimeField(
        'Дата создания',
        default=timezone.now)
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    parent = TreeForeignKey(
        'self',
        verbose_name="Родительская папка",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Папка'
        verbose_name_plural = 'Папки'


class File(models.Model):
    """Модель файлов"""
    label = models.CharField(
        'Название',
        max_length=255,
        default="no title")
    file = models.FileField(
        upload_to=file_path)
    share = models.UUIDField(
        unique=True,
        null=True,
        editable=True)
    filesize = models.PositiveIntegerField(
        'Размер файла',
        editable=False,
        default=1)
    date = models.DateTimeField(
        'Дата создания',
        default=timezone.now)
    user = models.ForeignKey(
        user,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    folder = models.ForeignKey(
        Folder,
        verbose_name='Папка',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    comment = models.CharField(
        'Комментарий к файлу',
        null=True,
        max_length=255,
    )
    url = models.URLField(
        'Ссылка на файл',
        null=True,
        max_length=1024,
    )

    def save(self, *args, **kwargs):
        super(File, self).save()
        fullpath = os.path.join(settings.MEDIA_ROOT, str(self.file))
        self.filesize = os.path.getsize(fullpath)
        super(File, self).save()

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
