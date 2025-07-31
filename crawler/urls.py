# from django.urls import path
# from rest_framework.authtoken.views import obtain_auth_token
from .views import *
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView , TokenVerifyView
# from django.conf import settings
# from django.conf.urls.static import static
# from django.views.generic import TemplateView

from django.urls import path, include

urlpatterns = [
    path('', crawler ,name='crawler'),
    path('v1/crawler-extractor/', crawler ,name='crawler'),
]