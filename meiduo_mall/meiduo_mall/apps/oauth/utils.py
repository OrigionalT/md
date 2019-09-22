from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings

oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state=next)
