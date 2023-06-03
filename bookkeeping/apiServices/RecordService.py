from api.models import *
from apiDao import UserDao, LedgerDao, LedgerAccessDao,RecordDao,ReceiptDao,SharePayDao
from django.db import transaction
from api.serializer import *
from apiServices import SharePayService
from datetime import datetime
import calendar #

class RecordService:
    UserDao = UserDao.UserDao()
    LedgerDao = LedgerDao.LedgerDao()
    LedgerAccessDao = LedgerAccessDao.LedgerAccessDao()
    RecordDao = RecordDao.RecordDao()
    ReceiptDao = ReceiptDao.ReceiptDao()
    SharePayDao=SharePayDao.SharePayDao()
    SharePayService=SharePayService.SharePayService()
    def __init__(self):
        pass
    
    def create_sharepay_record(self,user_param,record_param,ledger_param,user_payby_param,array_shareUsers):
        if(array_shareUsers == []):
            return {'status': 'fail', 'error': "shareUsers is NULL"}
        if(user_payby_param.UserID ==''):
            user_payby_param.UserID=user_param.UserID
        if(record_param.ItemType != "收入"):
            record_param.Cost=int(record_param.Cost)*(-1)
        if(record_param.BoughtDate == ''):
            record_param.BoughtDate = datetime.utcnow()
        record_param.LedgerID = self.LedgerDao.get_ledger_by_id(ledger_param)
        record_param.Payby = self.UserDao.get_user_by_id(user_payby_param.UserID)

        try:
            with transaction.atomic():
                record = self.RecordDao.create_record(record_param)
                self.SharePayService.add_sharepay_payby(record_param,record)
                self.SharePayService.add_sharepay_other(record_param,record,array_shareUsers)
        except Exception as e:
            return {'status': 'fail', 'error': 'Record creation failed'}
        return {'status': 'success', 'record': RecordSerializer(record).data}
    

    def delete_record(self,record_param):
        try:
            record = self.RecordDao.delete_record(record_param)
        except :
            return {'status': 'fail', 'error': 'Record deletion failed'}

        return {'status': 'success', 'record': RecordSerializer(record).data}
    

    def update_record(self, record_param , user_payby_param , array_shareUsers):

        record = self.RecordDao.get_record_by_id(record_param)
        if record is None:
            return {'status': 'fail', 'error': 'Record does not exist'}
        
        if (array_shareUsers == []):
            return {'status': 'fail', 'error': "shareUsers is NULL"}
        
        if record_param.ItemName != '':
            record.ItemName = record_param.ItemName

        #ItemType、Cost update
        if record_param.ItemType != '' and record_param.Cost != '':
            record.ItemType = record_param.ItemType
            cost = int(record_param.Cost)
            if(record.ItemType != "收入" and cost>0):
                cost=cost*(-1)
            record.Cost=cost
            record_param.Cost=cost
        elif record_param.ItemType != '':
            record.ItemType = record_param.ItemType
            cost=int(record.Cost)
            if(record.ItemType != "收入" and cost>0):
                cost=cost*(-1)
            elif(record.ItemType == "收入" and cost<0):
                cost=cost*(-1)
            record.Cost=cost
            record_param.Cost=record.Cost
        elif record_param.Cost != '':
            cost = int(record_param.Cost)
            if(record.ItemType != "收入" and cost>0):
                cost=cost*(-1)
            record.Cost=cost
            record_param.Cost=cost
        else:
            record_param.Cost=record.Cost

        if(user_payby_param.UserID != ''):
            record_param.Payby = self.UserDao.get_user_by_id(user_payby_param.UserID)
            record.Payby = record_param.Payby
        else:
            record_param.Payby = record.Payby
            user_payby_param = record.Payby

        if record_param.BoughtDate != '':
            record.BoughtDate = record_param.BoughtDate
        else:
            record_param.BoughtDate = record.BoughtDate
        
        receipt = self.ReceiptDao.get_receipt_by_recordID(record)
        print(receipt)
        if receipt != None:
                    receipt.BuyDate = record_param.BoughtDate
                    receipt = self.ReceiptDao.update_receipt(receipt)

        try:
            with transaction.atomic():
                self.SharePayDao.delete_sharepay(record)
                self.SharePayService.add_sharepay_payby(record_param,record)
                self.SharePayService.add_sharepay_other(record_param,record,array_shareUsers)
                record = self.RecordDao.update_record(record)

        except Exception as e:
            return {'status': 'fail', 'error': 'Record update failed'}
       
        return {'status': 'success', 'record': RecordSerializer(record).data,'receipt': ReceiptSerializer(receipt).data}
        
    def get_records_by_ledger(self,ledger_param):
        try:
            records = self.RecordDao.get_records_by_ledger(ledger_param)
        except :
            return {'status': 'fail', 'error': 'get_records_by_ledger failed'}

        return {'status': 'success', 'record': RecordSerializer(records, many=True).data}
    
    def get_this_month_ItemType_cost(self,user_param,record_param):
        ledgers =self.LedgerAccessDao.get_all_ledger_access_by_userID(user_param.UserID)
        Year = datetime.now().year
        Month = datetime.now().month
        end_day=calendar.monthrange(Year,int(Month))[1]
        start = str(Year)+'-'+str(Month)+"-1 00:00:00.000000"
        end = str(Year)+'-'+str(Month)+"-"+str(end_day)+" 23:59:59.999999"

        try:
            records= self.RecordDao.get_this_month_user_records_by_ItemType(ledgers,record_param,start,end)
            money=0
            for record in records:
                sharepays = self.SharePayDao.get_sharepay_by_recordID_and_userID(user_param,record)
                for share in sharepays:
                    if(record.ItemType !="收入" and share.ShouldPay<0):
                        money+=share.ShouldPay
                    elif(record.ItemType =="收入" and share.ShouldPay>0):
                        money+=share.ShouldPay
        except :
            return {'status': 'fail', 'error': 'get_this_month_ItemType_cost failed'}
       
        return {'status': 'success', 'this_month_ItemType_cost': money}
    
    def get_this_month_total_pay(self,user_param):
        ledgers =self.LedgerAccessDao.get_all_ledger_access_by_userID(user_param.UserID)
        Year = datetime.now().year
        Month = datetime.now().month
        end_day=calendar.monthrange(Year,int(Month))[1]
        start = str(Year)+'-'+str(Month)+"-1 00:00:00.000000"
        end = str(Year)+'-'+str(Month)+"-"+str(end_day)+" 23:59:59.999999"

        try:
            records= self.RecordDao.get_this_month_user_records_by_Pay(ledgers,start,end)
            money=0
            for record in records:
                sharepays = self.SharePayDao.get_sharepay_by_recordID_and_userID(user_param,record)
                for share in sharepays:
                    if(record.ItemType !="收入" and share.ShouldPay<0):
                        money+=share.ShouldPay
        except :
            return {'status': 'fail', 'error': 'get_this_month_total_pay failed'}

        return {'status': 'success', 'this_month_ItemType_cost': money}