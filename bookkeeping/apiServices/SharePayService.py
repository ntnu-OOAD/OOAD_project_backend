from api.models import *
from apiDao import UserDao, LedgerDao, LedgerAccessDao,RecordDao,SharePayDao
from django.db import transaction
from api.serializer import *

class SharePayService:
    UserDao = UserDao.UserDao()
    SharePayDao = SharePayDao.SharePayDao()
    def __init__(self):
        pass
    
    def add_sharepay_payby(self,record_param,record):
        sharepay_param = SharePay(
            ShouldPay = int(record_param.Cost)*(-1),
            RecordID = record,
            ShareUser = record_param.Payby
        )
        sharepay = self.SharePayDao.add_sharepay(sharepay_param)
        return sharepay

    def add_sharepay_other(self,record_param,record,array_shareUsers):
        l=0
        for item in array_shareUsers:
            l+=1
        cost=int(record_param.Cost)
        for item in array_shareUsers:
            sharepay_param = SharePay(
                ShouldPay = cost/l,
                RecordID = record,
                ShareUser = self.UserDao.get_user_by_id(item)
            )
            sharepay = self.SharePayDao.add_sharepay(sharepay_param) 
        return sharepay

    #def delete_sharepay(self,record_param)