from api.models import *
from api.serializer import *
from django.db.models import Q, F

class SharePayDao:
    @staticmethod
    def add_sharepay(sharepay_param):
        sharepay = SharePay.objects.create(
            RecordID=sharepay_param.RecordID, 
            ShouldPay=sharepay_param.ShouldPay, 
            ShareUser =sharepay_param.ShareUser )
        sharepay.save()
        return sharepay
    
    @staticmethod
    def delete_sharepay(record_param):
        sharepay=SharePay.objects.filter(RecordID = record_param.RecordID)
        sharepay.delete()  
        return record_param
    
    @staticmethod
    def get_sharepay_by_recordID_and_userID(user_param,record_parm):
        sharepays = SharePay.objects.filter(Q(RecordID = record_parm.RecordID)& Q(ShareUser=user_param.UserID))
        return sharepays
    
    @staticmethod
    def get_sharepay_by_ledger(record,userID):
        sharepay_filter = Q()
        for sharepay_arr in record:
            sharepay_filter = sharepay_filter | (Q(RecordID = sharepay_arr.RecordID) & Q( ShareUser = userID))
        sharepays = SharePay.objects.filter(sharepay_filter)
        return sharepays
    
    @staticmethod
    def get_sharepay_by_recordID(record_param):
        sharepays = SharePay.objects.filter(RecordID=record_param.RecordID)
        return sharepays
    



