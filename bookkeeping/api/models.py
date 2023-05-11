from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime

class CustomUserManager(BaseUserManager):
    def create_user(self, UserName, UserNickname, password):
        """
        Creates and saves a User with the given email and password.
        """
        if not UserName:
            raise ValueError('The UserName field must be set')
        user = self.model(UserName=UserName, UserNickname=UserNickname)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, UserName, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.model(UserName=UserName)
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    UserID = models.BigAutoField(primary_key=True)
    UserName = models.CharField(max_length=320, blank=False, unique=True)
    UserNickname = models.CharField(max_length=320, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'UserName'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.UserName

    def get_full_name(self):
        return self.UserName

    def get_short_name(self):
        return self.UserName

class Ledger(models.Model):
    LedgerID = models.BigAutoField(primary_key=True)
    LedgerName = models.TextField(max_length=320 , default = "None")
    OwnerID = models.ForeignKey(User, on_delete=models.CASCADE)
    LedgerType = models.TextField(max_length=320 , default = "None")
    CreateDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.LedgerName
    

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
    Payby = models.ForeignKey(User, on_delete=models.CASCADE)
    BoughtDate = models.DateTimeField(default=datetime.now)

class SharePay(models.Model):
    RecordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    ShareUser = models.ForeignKey(User, on_delete=models.CASCADE)
    ShouldPay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.RecordID

class Receipt(models.Model):
    ReceiptID = models.BigAutoField(primary_key=True)
    RecordID = models.ForeignKey(Record, on_delete=models.CASCADE)
    BuyDate = models.DateTimeField(default = "None")
    StatusCode = models.TextField(max_length=320 , default = "None")