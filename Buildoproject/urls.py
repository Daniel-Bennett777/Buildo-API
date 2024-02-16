from django.contrib import admin
from django.urls import include, path
from Buildoapi.views.users import UserViewSet
from Buildoapi.views import ConnectionRequestViewSet, ConnectionViewSet, JobRequestViewSet, ReviewViewSet, WorkOrderViewSet,ContractorViewSet
from Buildoapi.views import MessagesView
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'work_orders', WorkOrderViewSet,"work_order")
router.register(r'reviews', ReviewViewSet,'review')
router.register(r'contractors_list', ContractorViewSet, basename='contractors')
router.register(r'job_requests', JobRequestViewSet, basename='job-requests')
router.register(r'connection_requests', ConnectionRequestViewSet, basename='connection_requests')
router.register(r'connections', ConnectionViewSet, basename='connections')
router.register(r'messages', MessagesView, 'messages')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserViewSet.as_view(
        {'post': 'register_account'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login_user'}), name='login'),
    path('reviews/<int:contractorId>/', ReviewViewSet.as_view({'get': 'list'}), name='reviews-contractor'),
]


