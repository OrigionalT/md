import re

from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from celery_tasks.email.tasks import send_verify_email
from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.BooleanField(label='同意协议勾选', write_only=True)
    token = serializers.CharField(label="jwt", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'allow', 'mobile', 'token')

        extra_kwargs = {
            'password': {
                'min_length': 6,
                'max_length': 20
            },
            'password2': {
                'min_length': 6
            },
        }

    def validate(self, attrs):
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        allow = attrs.get('allow')

        if password != password2:
            raise serializers.ValidationError({'message': '密码不一致'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise serializers.ValidationError({'message': '手机号有误'})

        redis_conn = get_redis_connection('verify_codes')

        redis_sms_code = redis_conn.get("sms_%s" % mobile)

        if redis_sms_code is None:
            raise serializers.ValidationError({"message": "验证码已过期"})
        if redis_sms_code.decode() != sms_code:
            raise serializers.ValidationError({"message": "验证码错误"})
        if not allow:
            raise serializers.ValidationError({'message': '未勾选同意'})

        return attrs

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 创建新用户
        user = User.objects.create_user(**validated_data)

        # 设置最新登录时间
        user.last_login = timezone.now()
        user.save()

        # 生成jwt token，保存用户的身份信息
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 给user增加token属性，保存jwt token的信息
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户中心"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')

# class UserLoginSerializer(serializers.ModelSerializer):
#     token = serializers.CharField(label="jwt", read_only=True)
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'token')
#
#     def validate(self, attrs):
#         # 获取username和password
#         username = attrs['username']
#         password = attrs['password']
#         # 进行用户名和密码校验
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             raise serializers.ValidationError('用户名或密码错误')
#         else:
#             # 校验密码
#             if not user.check_password(password):
#                 raise serializers.ValidationError('用户名或密码错误')
#
#             # 给attrs中添加user属性，保存登录用户
#             attrs['user'] = user
#             attrs['user_id'] = user.id
#
#         return attrs
#
#     def create(self, validated_data):
#         # 获取登录用户user
#         user = validated_data['user']
#
#         # 设置最新登录时间
#         user.last_login = timezone.now()
#         user.save()
#
#         # 组织payload数据的方法
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#         # 生成jwt token数据的方法
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#
#         # 组织payload数据
#         payload = jwt_payload_handler(user)
#         # 生成jwt token
#         token = jwt_encode_handler(payload)
#
#         # 给user对象增加属性，保存jwt token的数据
#         user.token = token
#
#         return user


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')

    def update(self, instance, validated_data):

        """发送邮件"""
        email = validated_data.get('email')
        instance.email = email
        instance.save()
        verify_url = instance.generate_verify_email_url()
        send_verify_email.delay(email,verify_url)

        return instance
