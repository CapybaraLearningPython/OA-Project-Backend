from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField

class UserStatusChoices(models.IntegerChoices):
    ACTIVATED = 1
    UNACTIVATED = 2
    LOCKED = 3
 
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, name, email, password, **extra_fields):
        if not name:
            raise ValueError("必须提供员工姓名！")
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, name, email, password, **extra_fields):
        user = self._create_user_object(name, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置为员工身份！")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须拥有超级用户的权限！")

        return self._create_user(name, email, password, **extra_fields)
   

class OAUser(AbstractBaseUser, PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=True)
    status = models.IntegerField(
        choices=UserStatusChoices.choices, 
        default=UserStatusChoices.UNACTIVATED
    )
    date_joined = models.DateField(auto_now_add=True)
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        related_name='crew', 
        null=True
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "password"]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
    class Meta:
        ordering = ['-date_joined']
        
class Department(models.Model):
    name = models.CharField(max_length=200)
    leader = models.OneToOneField(
        OAUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='my_department'
    )
    manager = models.ForeignKey(
        OAUser, on_delete=models.SET_NULL, 
        related_name="departments", 
        null=True
    )