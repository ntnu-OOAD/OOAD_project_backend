from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['UserID', 'UserName', 'UserNickname']

class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['LedgerID', 'LedgerName', 'OwnerID', 'LedgerType', 'CreateDate']

class LedgerAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccess
        fields = ['LedgerID', 'UserID', 'AccessLevel']

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ['RecordID', 'LedgerID', 'ItemName', 'ItemType', 'Cost', 'Payby', 'BoughtDate']

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['ReceiptID', 'RecordID', 'BuyDate', 'StatusCode']
class SharePaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SharePay
        fields = ['ShouldPay', 'RecordID', 'ShareUser']
