import logging

from django.contrib.auth import get_user_model
from django.http import FileResponse
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .models import File, Folder
from django.contrib.auth.models import User, Group
from django.conf import settings

from django.contrib.auth import authenticate
from djoser.conf import settings
from djoser.serializers import TokenCreateSerializer

user = get_user_model()
logging.basicConfig(level=logging.INFO, filename="my_cloud.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


class FileSerializer(serializers.ModelSerializer):
    label = serializers.CharField(read_only=True)
    date = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M')
    filesize = serializers.IntegerField(read_only=True)
    share = serializers.UUIDField(read_only=True)
    url = serializers.URLField(read_only=True)
    # folder = serializers.IntegerField(read_only=True)
    # user = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        validated_data['label'] = validated_data.get('file')
        validated_data['user'] = self.context['request'].user
        logging.info(f"Загружен новый файл: {validated_data['file']} пользователем: {self.context['request'].user}")
        print(f"Загружен новый файл: {validated_data['file']} пользователем: {self.context['request'].user}")
        return File.objects.create(**validated_data)

    class Meta:
        model = File
        fields = '__all__'


class UserFileSerializer(serializers.ModelSerializer):
    label = serializers.CharField(read_only=True)
    date = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M')
    filesize = serializers.IntegerField(read_only=True)
    share = serializers.UUIDField(read_only=True)
    url = serializers.URLField(read_only=True)

    def create(self, validated_data):
        validated_data['label'] = validated_data.get('file')
        validated_data['user'] = User.objects.get(username=self.context['request'].query_params['username'])
        logging.info(f"Загружен новый файл: {validated_data['file']} пользователем: {self.context['request'].user}")
        print(f"Загружен новый файл: {validated_data['file']} пользователем: {self.context['request'].user}")
        return File.objects.create(**validated_data)

    class Meta:
        model = File
        fields = '__all__'


class FileDetailSerializer(serializers.ModelSerializer):
    filesize = serializers.IntegerField(read_only=True)
    file = serializers.FileField(read_only=True)
    uuid = serializers.UUIDField(format="hex", read_only=True)
    date = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M')
    user = serializers.CharField(max_length=100, read_only=True)
    share = serializers.UUIDField(read_only=True)
    url = serializers.URLField(read_only=True)

    class Meta:
        model = File
        fields = '__all__'


class FileShareUrlSerializer(serializers.ModelSerializer):
    filesize = serializers.IntegerField(read_only=True)
    file = serializers.FileField(read_only=True)
    share = serializers.UUIDField(read_only=True)
    date = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M')
    user = serializers.CharField(max_length=100, read_only=True)
    label = serializers.CharField(read_only=True)
    comment = serializers.CharField(read_only=True)
    folder = serializers.CharField(read_only=True)
    url = serializers.URLField(read_only=True)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()
        logging.info(f'uuid для файла {instance} сгенерирован')
        print(f'uuid для файла {instance} сгенерирован')
        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    class Meta:
        model = File
        fields = '__all__'


def download(request, id):
    obj = File.objects.get(id=id)
    filename = obj.file.path
    response = FileResponse(open(filename, 'rb'))
    return response


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class FolderSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'label', 'date', 'parent', 'user',)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    last_login = serializers.DateTimeField(read_only=True, format='%d-%m-%Y, %H:%M')

    class Meta:
        model = get_user_model()
        fields = ['url', 'username', 'first_name', 'last_name', 'password', 'email', 'groups', 'last_login', 'is_staff',
                  'is_superuser', 'is_active', ]


class UserChanger(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['is_superuser']


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.LOGIN_FIELD: attrs.get(settings.LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user:
            return attrs
        self.fail("invalid_credentials")