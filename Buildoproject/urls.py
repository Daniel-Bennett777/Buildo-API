from django.contrib import admin
from django.urls import include, path
from Buildoapi.views.users import UserViewSet
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view(
        {'post': 'register_account'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login_user'}), name='login'),
]


