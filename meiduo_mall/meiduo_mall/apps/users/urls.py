from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views
urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UserCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    url(r'^users/$',views.UserRegisterView.as_view()),
    # url(r'^authorizations/$',views.UserLoginView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^email/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]
