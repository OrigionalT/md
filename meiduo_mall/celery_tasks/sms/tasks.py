import logging

from celery_tasks.main import celery_app

from celery_tasks.yuntongxun.sms import CCP

logger = logging.getLogger("django")
#
# # 验证码短信模板
# SMS_CODE_TEMP_ID = 1
#
#
# @celery_app.task(name='send_sms_code')
# def send_sms_code(mobile, code, expires):
#     """
#     发送短信验证码
#     :param mobile: 手机号
#     :param code: 验证码
#     :param expires: 有效期
#     :return: None
#     """
#     try:
#         ccp = CCP()
#         result = ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)
#     except Exception as e:
#         logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
#     else:
#         if result == 0:
#             logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
#         else:
#             logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
def ccp_send_sms_code(self, mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或 失败-1
    """

    try:
        # 调用 CCP() 发送短信, 并传递相关参数:
        result = CCP().send_template_sms(mobile,
                                         [sms_code, 5],
                                         1)

    except Exception as e:
        # 如果发送过程出错, 打印错误日志
        logger.error(e)

        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)

       # 如果发送成功, rend_ret 为 0:
    if result != 0:
        # 有异常自动重试三次
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)

    return result
