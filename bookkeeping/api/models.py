from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, nickname, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('The username field must be set')
        user = self.model(username=username, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, nickname, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=320, unique=True, blank=False)
    nickname = models.CharField(max_length=320, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    is_active = True
    is_staff = None
    groups = None
    user_permissions = None
    is_superuser  = None
    last_login = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.nickname

class Ledger(models.Model):
    LedgerID = models.BigAutoField(primary_key=True)
    OwnerID = models.ForeignKey(User, on_delete=models.CASCADE)
    Type = models.TextField(max_length=320 , default = "None")
    CreateDate = models.DateTimeField(auto_now_add=True)

class LedgerAccess(models.Model):
    LedgerID = models.ForeignKey(Ledger, on_delete=models.CASCADE)
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    AccessLevel = models.TextField(max_length=320 , default = "None")

class Record(models.Model):
    RecordID = models.BigAutoField(primary_key=True)
    LedgerID = models.ForeignKey(Ledger, on_delete=models.CASCADE)
    ItemName = models.TextField(max_length=320 , default = "None")
    ItemType = models.TextField(max_length=320 , default = "None")
    Cost = models.DecimalField(max_digits=10, decimal_places=2)
    Payby = models.TextField(max_length=320 , default = "None")

class SharePay(models.Model):
    RecordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    ShareUser = models.ForeignKey(User, on_delete=models.CASCADE)
    ShouldPay = models.DecimalField(max_digits=10, decimal_places=2)

class Receipt(models.Model):
    ReceiptID = models.BigAutoField(primary_key=True)
    RecordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    BuyDate = models.DateTimeField(default = "None")
    StatusCode = models.TextField(max_length=320 , default = "None")