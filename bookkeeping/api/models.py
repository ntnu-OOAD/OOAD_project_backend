from django.db import models

# Create your models here.
class User(models.Model):
    UserID = models.BigAutoField(primary_key=True)
    Username = models.TextField(max_length=320 , default = "None")
    Email = models.TextField(max_length=320 , default = "None")
    CreateDate = models.DateTimeField(auto_now_add=True)

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