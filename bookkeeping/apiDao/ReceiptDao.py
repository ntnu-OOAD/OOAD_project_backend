from api.models import *
from api.serializer import *
from django.db.models import Q, F

class ReceiptDao:

    @staticmethod
    def update_receipt(receipt_param):
        receipt_param.save()
        return receipt_param

    @staticmethod
    def get_receipt_by_recordID(record_param):
        try:
            receipt = Receipt.objects.filter(RecordID=record_param.RecordID).first()
            return receipt
        except:
            return None