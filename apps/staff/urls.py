from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', views.StaffViewSet, basename='staff')

app_name = 'staff'
urlpatterns = [
    path('get_departments/', views.DepartmentView.as_view(), name='get_departments'),
    path('activation/', views.EmployeeActivationView.as_view(), name='activation'),
    path('upload/', views.StaffUploadView.as_view(), name='upload'),
    path('download/', views.StaffDownloadView.as_view(), name='download')
]+router.urls

print(urlpatterns)