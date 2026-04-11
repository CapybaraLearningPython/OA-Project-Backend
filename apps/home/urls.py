from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('latest_leave_requests/', views.LatestLeaveRequestsView.as_view(), name='latest_leave_requests'),
    path('latest_notifications/', views.LatestNotificationsView.as_view(), name='latest_notifications'),
    path('staff_count/', views.StaffCountView.as_view(), name='staff_count'),
]
