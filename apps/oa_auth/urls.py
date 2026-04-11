from django.urls import path
from . import views

app_name = "oa_auth"
urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('change_pwd/', views.ChangePasswordView.as_view(), name="change_pwd"),
]