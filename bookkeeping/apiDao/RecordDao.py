from api.models import *
from api.serializer import *
from django.db.models import Q, F

class RecordDao:

    @staticmethod
    def create_record(record_param):
        record = Record.objects.create(
            LedgerID=record_param.LedgerID, 
            ItemName=record_param.ItemName, 
            ItemType=record_param.ItemType, 
            Cost=record_param.Cost, 
            Payby=record_param.Payby, 
            BoughtDate=record_param.BoughtDate)
        record.save()
        return record
    
    @staticmethod
    def delete_record(record_param):
        record = Record.objects.get(RecordID=record_param.RecordID)
        record.delete()
        return record
    
    @staticmethod
    def update_record(record_param):
        record_param.save()
        return record_param
    
    @staticmethod
    def get_record_by_id(record_param):
        try:
            record = Record.objects.filter(RecordID=record_param.RecordID).first()
            return record
        except:
            return None
        
    @staticmethod
    def get_records_by_ledger(ledger_param):
        records = Record.objects.filter(LedgerID=ledger_param.LedgerID)
        return records
    
    @staticmethod
    def get_this_month_user_records_by_ItemType(ledgers,record_param,start,end):
        record_filter = Q()
        for ledger in ledgers:
            record_filter = record_filter | Q(LedgerID=ledger.LedgerID) 
        records=Record.objects.filter(record_filter & Q(ItemType=record_param.ItemType) & Q(BoughtDate__range=(start,end)))
        return records
    
    @staticmethod
    def get_this_month_user_records_by_Pay(ledgers,start,end):
        record_filter = Q()
        for ledger in ledgers:
            record_filter = record_filter | Q(LedgerID=ledger.LedgerID) 
        records=Record.objects.filter(record_filter & ~Q(ItemType="收入") & Q(BoughtDate__range=(start,end)))
        return records
    
