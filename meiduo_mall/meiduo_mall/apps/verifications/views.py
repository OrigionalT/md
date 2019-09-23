import random

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from celery_tasks.sms.tasks import ccp_send_sms_code

from . import constants


class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 连接redis
        redis_conn = get_redis_connection('verify_codes')
        # 避免频繁点击
        send_flag = redis_conn.get("send_flag")
        if send_flag:
            return Response({'message': '请求次数过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        print(sms_code)
        # 创建redis管道对象
        pl = redis_conn.pipeline()
        # 保存短信验证码与send_flag
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道
        pl.execute()

        # try:
        #     ccp = CCP()
        #
        #     ccp.send_template_sms(mobile, ['123456', constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
        # except Exception as e:
        #     return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        ccp_send_sms_code.delay(mobile, sms_code)

        return Response({'message': 'OK'})
