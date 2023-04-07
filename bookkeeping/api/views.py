from .models import *
from rest_framework import viewsets,permissions
from .serializer import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'status': 'success'})
        else:
            return Response({'status': 'fail'})
    @action(detail=False, methods=['post'])
    def logout(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return Response({'status': 'fail', 'error': 'user not logged in'})
        logout(request)
        return Response({'status': 'success'})
    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data['username']
        nickname = request.data['nickname']
        password = request.data['password']
        # check if username is already taken
        if User.objects.filter(username=username).exists():
            return Response({'status': 'fail', 'error': 'username already taken'})
        password = make_password(password, None, 'pbkdf2_sha256')
        user = User.objects.create_user(username=username, nickname=nickname, password=password)
        user.save()
        return Response({'status': 'success'})
    @action(detail=False, methods=['get'])
    def get_user(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return Response({'status': 'fail', 'error': 'user not logged in'})
        user = User.objects.get(username=request.user.username)
        return Response({'status': 'success', 'user': UserSerializer(user).data})