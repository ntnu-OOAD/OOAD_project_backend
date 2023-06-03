from api.models import *
from apiDao import UserDao, LedgerDao, LedgerAccessDao,RecordDao,SharePayDao
from django.db import transaction
from api.serializer import *

class SharePayService:
    UserDao = UserDao.UserDao()
    LedgerDao=LedgerDao.LedgerDao()
    RecordDao = RecordDao.RecordDao()
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

    def get_sharepay_by_ledger(self,ledger_param):
        records = self.RecordDao.get_records_by_ledger(ledger_param)
        if (records.count() == 0):
            return {'status': 'fail', 'error': 'This ledger does not has Record'}
        result = self.LedgerDao.get_ledger_info(ledger_param, with_access_level= "true")
        #result= result['ledger_with_access']
        result= result['users_access_list']

        sharepay_result={'sharepay':[]}
        for array in result:
            userID= array['UserID']
            sharepays = self.SharePayDao.get_sharepay_by_ledger(records,userID)
            money=0
            for arr in sharepays:
                money+=arr.ShouldPay
            sharepay_result['sharepay'].append({'UserID':userID,'UserName':array['UserName'],'Share_money':money})
        return {'status': 'success','result':sharepay_result}
    
    def get_sharepay_by_record(self,record_param):
        record = self.RecordDao.get_record_by_id(record_param)
        if record is None:
            return {'status': 'fail', 'error': 'Record does not exist'}
        
        sharepays = self.SharePayDao.get_sharepay_by_recordID(record_param)
        if(sharepays.count() == 0):
            return {'status': 'fail', 'error': 'SharePay does not exist'}
        
        ledger_param = Ledger(
            LedgerID = record.LedgerID.LedgerID
        )
        result = self.LedgerDao.get_ledger_info(ledger_param, with_access_level= "true")
        #result= result['ledger_with_access']
        result= result['users_access_list']
        sharepay_result={'sharepay':[]}

        for array in result:
            user_param= User(
                UserID = array['UserID']
            )
            sharepays = self.SharePayDao.get_sharepay_by_recordID_and_userID(user_param,record_param)
            money=0
            for arr in sharepays:
                if(record.ItemType!="收入" and arr.ShouldPay<0):
                    money+=arr.ShouldPay
                elif(record.ItemType == "收入" and arr.ShouldPay>0):
                    money+=arr.ShouldPay
            sharepay_result['sharepay'].append({'UserID':array['UserID'],'UserName':array['UserName'],'Share_money':money})
        return {'status': 'success','result':sharepay_result}
    
    def get_sharepay_user_by_record(self,record_param):
        record = self.RecordDao.get_record_by_id(record_param)
        if record is None:
            return {'status': 'fail', 'error': 'Record does not exist'}
        
        sharepays = self.SharePayDao.get_sharepay_by_recordID(record_param)
        if(sharepays.count() == 0):
            return {'status': 'fail', 'error': 'SharePay does not exist'}
        
        ledger_param = Ledger(
            LedgerID = record.LedgerID.LedgerID
        )
        result = self.LedgerDao.get_ledger_info(ledger_param, with_access_level= "true")
        #result= result['ledger_with_access']
        result= result['users_access_list']
        sharepay_result={'ShareUsers':[]}

        for array in result:
            user_param= User(
                UserID = array['UserID']
            )
            sharepays = self.SharePayDao.get_sharepay_by_recordID_and_userID(user_param,record_param)
            money=0
            for arr in sharepays:
                if(record.ItemType!="收入" and arr.ShouldPay<0):
                    money+=arr.ShouldPay
                elif(record.ItemType == "收入" and arr.ShouldPay>0):
                    money+=arr.ShouldPay
            if(money!=0):
                sharepay_result['ShareUsers']+=[array['UserID']]
        return {'status': 'success','ShareUsers':sharepay_result.get('ShareUsers')}
