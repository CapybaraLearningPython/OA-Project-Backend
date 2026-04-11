from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', views.AttendanceViewset, basename='attendance')

app_name = 'attendance'
urlpatterns = [
    path('leave_types/', views.LeaveTypeView.as_view(), name='leave_types')    
] + router.urls