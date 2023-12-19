import os
import logging
import datetime

from django.shortcuts import render
from django.utils import timezone
import uuid
from django.contrib.auth.hashers import make_password
from rest_framework import generics, viewsets, permissions, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from crud_2003.settings import BASE_DIR
from .models import File, Folder
from .serializers import FileSerializer, UserSerializer, GroupSerializer, FileDetailSerializer, FolderSerializer, \
    FileShareUrlSerializer, UserChanger, UserFileSerializer
from django.contrib.auth.models import User, Group
from django.http import FileResponse
from rest_framework.authtoken.models import Token
from django.conf import settings

logging.basicConfig(level=logging.INFO, filename="my_cloud.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def index(request):
    return render(request, str(BASE_DIR) + '\\files\\templates\\index.html')


class FileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileDetailSerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()

    def get(self, request, *args, **kwargs):
        logging.info(f"Выбран файл: {File.objects.get(id=self.kwargs['pk'])}")
        print(f"Выбран файл: {File.objects.get(id=self.kwargs['pk'])}")
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        old_label_file = File.objects.get(id=self.kwargs['pk'])
        path_to_file = old_label_file.file
        filename_in_field = str(path_to_file).split('/')[-1]
        self.update(request, *args, **kwargs)
        instance = File.objects.get(id=self.kwargs['pk'])
        file_dir = f"{os.getcwd()}\\files\\storages"
        ids = request.user.id
        os.rename(f'{file_dir}\\{ids}\\{filename_in_field}', f'{file_dir}\\{ids}\\{instance}')
        instance.file.name = f"files/storages/{ids}/{request.data['label']}"
        instance.save()
        logging.info(f"Имя файла: [{filename_in_field}] обновлено на: [{request.data['label']}]")
        print(f"Имя файла: [{filename_in_field}] обновлено на: [{request.data['label']}]")
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        label_file = File.objects.get(id=self.kwargs['pk'])
        path_to_file = label_file.file
        filename_in_field = str(path_to_file).split('/')[-1]
        ids = request.user.id
        file_dir = os.getcwd() + '\\files\\storages\\' + str(ids)
        File.objects.filter(id=self.kwargs['pk']).delete()
        os.remove(str(file_dir) + '\\' + str(filename_in_field))
        print('Удалён файл: ' + str(filename_in_field))
        logging.info('Удалён файл: ' + str(filename_in_field))
        return self.destroy(request, *args, **kwargs)


class FileDetailUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileDetailSerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()

    def get(self, request, *args, **kwargs):
        logging.info(f"Выбран файл: {File.objects.get(id=self.kwargs['pk'])}")
        print(f"Выбран файл: {File.objects.get(id=self.kwargs['pk'])}")
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        user_list = request.GET.get('user_list')
        find_username = User.objects.get(username=user_list)
        old_label_file = File.objects.get(id=self.kwargs['pk'])
        path_to_file = old_label_file.file
        filename_in_field = str(path_to_file).split('/')[-1]
        self.update(request, *args, **kwargs)
        instance = File.objects.get(id=self.kwargs['pk'])
        file_dir = f"{os.getcwd()}\\files\\storages"
        ids = find_username.id
        os.rename(f'{file_dir}\\{ids}\\{filename_in_field}', f'{file_dir}\\{ids}\\{instance}')
        instance.file.name = f"files/storages/{ids}/{request.data['label']}"
        instance.save()
        logging.info(f"Имя файла: [{filename_in_field}] обновлено на: [{request.data['label']}]")
        print(f"Имя файла: [{filename_in_field}] обновлено на: [{request.data['label']}]")
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user_list = request.GET.get('user_list')
        find_username = User.objects.get(username=user_list)
        label_file = File.objects.get(id=self.kwargs['pk'])
        path_to_file = label_file.file
        filename_in_field = str(path_to_file).split('/')[-1]
        ids = find_username.id
        file_dir = os.getcwd() + '\\files\\storages\\' + str(ids)
        File.objects.filter(id=self.kwargs['pk']).delete()
        os.remove(str(file_dir) + '\\' + str(filename_in_field))
        print('Удалён файл: ' + str(filename_in_field))
        logging.info('Удалён файл: ' + str(filename_in_field))
        return self.destroy(request, *args, **kwargs)


class ShareUrlAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = FileShareUrlSerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()

    def get(self, request, *args, **kwargs):
        print(f"Для создания uuid выбран следующий файл: {File.objects.get(id=self.kwargs['pk'])}")
        logging.info(f"Для создания uuid выбран следующий файл: {File.objects.get(id=self.kwargs['pk'])}")
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = File.objects.get(id=self.kwargs['pk'])
        instance.share = uuid.uuid4()
        logging.info(f"Ссылка создана: {request.build_absolute_uri('/')}file/download/?share={instance.share}")
        print(f"Ссылка создана: {request.build_absolute_uri('/')}file/download/?share={instance.share}")
        instance.url = f"{request.build_absolute_uri('/')}file/download/?share={instance.share}"
        instance.save()
        return self.update(request, *args, **kwargs)


class RemoveShareUrlAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = FileShareUrlSerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()

    def put(self, request, *args, **kwargs):
        instance = File.objects.get(id=self.kwargs['pk'])
        instance.share = None
        instance.url = None
        instance.save()
        logging.info(f"Ссылка на файл [{instance}] удалена.")
        print(f"Ссылка на файл [{instance}] удалена.")
        return self.update(request, *args, **kwargs)


def download_share(request):
    file_uuid = request.GET.get('share')
    obj = File.objects.get(share=file_uuid)
    filename = obj.file.path
    response = FileResponse(open(filename, 'rb'))
    return response


class FilesListFolder(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        req_user_name = User.objects.get(username=self.request.user)
        logging.info(f'Обзор списка файлов пользователем: [{req_user_name}]')
        print(f'Обзор списка файлов пользователем: "{req_user_name}"')
        return self.queryset.filter(user=req_user_name)

    def post(self, request, *args, **kwargs):
        req_user_name = User.objects.get(username=self.request.user)
        instance = User.objects.get(username=req_user_name)
        return self.create(request, *args, **kwargs)


class UserFilesListFolder(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()
    serializer_class = UserFileSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        username_storage = self.request.GET.get('username')
        req_user_name = User.objects.get(username=username_storage)
        logging.info(f'Обзор списка файлов пользователя: [{username_storage}]')
        print(f'Обзор списка файлов пользователя: "{username_storage}"')
        return self.queryset.filter(user=req_user_name)

    def post(self, request, *args, **kwargs):
        req_user_name = User.objects.get(username=self.request.user)
        instance = User.objects.get(username=req_user_name)
        return self.create(request, *args, **kwargs)


class AuthUser(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        quantity_files = len(File.objects.filter(user=self.request.user))
        req_user_name = User.objects.get(username=self.request.user)
        timezone.make_aware(datetime.datetime.now(),
                            timezone=timezone.get_current_timezone())
        req_user_name.last_login = timezone.make_aware(datetime.datetime.now(),
                                                       timezone=timezone.get_current_timezone())

        req_user_name.save()
        all_users = [users for users in User.objects.values("id",
                                                            "username",
                                                            "last_login",
                                                            "email",
                                                            "is_superuser",
                                                            "is_active",
                                                            "first_name",
                                                            "last_name", )]

        is_admin_user = {"auth": True, "userInfo": {"admin": req_user_name.is_superuser,
                                                    "name": req_user_name.username,
                                                    "firstName": req_user_name.first_name,
                                                    "lastName": req_user_name.last_name,
                                                    "email": req_user_name.email,
                                                    "lastLogin": req_user_name.last_login,
                                                    "userId": request.user.id,
                                                    "quantityFiles": quantity_files},
                         "allUsers": ""}

        if req_user_name:
            logging.info(f'Авторизовался пользователь под ником: {req_user_name}')
            print(f'Авторизовался пользователь под ником: {req_user_name}')
            if req_user_name.is_superuser:
                is_admin_user['allUsers'] = all_users
                return Response(is_admin_user)
            else:
                is_admin_user['allUsers'] = ''
                return Response(is_admin_user)


class CountFiles(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        quantity_files = len(File.objects.filter(user=self.request.user))
        return Response({"count_files": quantity_files})


class UpdateUserParams(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserChanger


class FileNullFolderApiView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(folder=None)


class FileListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(folder=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save()


class FolderApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FolderNullParentApiView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(parent=None)


class FoldersListApiView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (BasicAuthentication, SessionAuthentication,)
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token = Token.objects.create(user=serializer.instance)
        token_data = {"token": token.key}
        return Response(
            {**serializer.data, **token_data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()
        logging.info(f'Зарегистрирован новый пользователь: {serializer.data["username"]}')
        print(f'Зарегистрирован новый пользователь: {serializer.data["username"]}')

    def perform_update(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()
        logging.info(f'Данные пользователя: {serializer.data["username"]} обновлены')
        print(f'Данные пользователя: {serializer.data["username"]} обновлены')


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class FolderListCreateApiView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def perform_create(self, serializer):
        serializer.save()
