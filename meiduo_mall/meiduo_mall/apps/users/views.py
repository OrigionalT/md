from rest_framework.generics import CreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserRegisterSerializer, UserDetailSerializer, EmailSerializer  # UserLoginSerializer
from rest_framework.permissions import IsAuthenticated

# GET usernames/(?P<username>\w{5,20})/count/
class UserCountView(APIView):
    """查看用户名是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# GET mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserRegisterView(CreateAPIView):
    """创建用户"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


# POST /authorizations/
# class UserLoginView(CreateAPIView):
#     """用户登录"""
#     queryset = User.objects.all()
#     serializer_class = UserLoginSerializer
class UserDetailView(RetrieveAPIView):
    """用户中心"""
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    #
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """保存邮箱"""
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user

