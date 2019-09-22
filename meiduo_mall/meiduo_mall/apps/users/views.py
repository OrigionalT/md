from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserRegisterSerializer # UserLoginSerializer


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
