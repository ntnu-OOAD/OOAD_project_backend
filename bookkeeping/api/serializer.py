from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['UserID', 'nickname', 'password']

class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['LedgerID', 'OwnerID', 'Type', 'CreateDate']

class LedgerAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccess
        fields = ['LedgerID', 'UserID', 'AccessLevel']