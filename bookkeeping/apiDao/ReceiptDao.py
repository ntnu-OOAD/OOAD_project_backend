from api.models import *
from api.serializer import *
from django.db.models import Q, F

class ReceiptDao:

    @staticmethod
    def add_receipt(receipt_param):
        receipt = Receipt.objects.create(
            RecordID=receipt_param.RecordID, 
            BuyDate = receipt_param.BuyDate,
            StatusCode = receipt_param.StatusCode
            )
        receipt.save()
        return receipt
    
    @staticmethod
    def delete_receipt(receipt_param):
        receipt_param.delete()
        return receipt_param

    @staticmethod
    def update_receipt(receipt_param):
        receipt_param.save()
        return receipt_param
    
    @staticmethod
    def get_receipt_by_id(receipt_param):
        try:
            receipt = Receipt.objects.filter(ReceiptID=receipt_param.ReceiptID).first()
            return receipt
        except:
            return None
        
    @staticmethod
    def get_receipt_by_recordID(record_param):
        try:
            receipt = Receipt.objects.filter(RecordID=record_param.RecordID).first()
            return receipt
        except:
            return None
        
    @staticmethod
    def get_receipts_by_records(records):
        receipt_filter = Q()
        for record in records:
             receipt_filter = receipt_filter | Q(RecordID=record.RecordID)
        receipts=Receipt.objects.filter(receipt_filter)
        return receipts
    
    @staticmethod
    def get_receipts_by_records_and_date(records,start,end):
        receipt_filter = Q()
        for record in records:
            receipt_filter = receipt_filter | (Q(RecordID=record.RecordID)& Q(BuyDate__range=(start,end)))
        receipts=Receipt.objects.filter(receipt_filter)
        return receipts
    
    @staticmethod
    def get_receipt_by_records_and_date(record,start,end):
        try:
            receipt=Receipt.objects.filter(Q(RecordID=record.RecordID)& Q(BuyDate__range=(start,end))).first()
            return receipt
        except:
            return None