from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from . import views

router = DefaultRouter()
router.register('', views.NotificationViewSet, basename='notifications')

app_name = 'notifications'
urlpatterns = [
    path('status/', views.NotificationStatusView.as_view(), name='notification_status')
] + router.urls