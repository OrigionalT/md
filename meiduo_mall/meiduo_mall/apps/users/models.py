from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer, BadData


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 10)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email(token):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 10)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
