from api.models import *
from django.db import transaction
from api.serializer import *
from apiDao import UserDao, LedgerDao, LedgerAccessDao,RecordDao,ReceiptDao,SharePayDao
import requests
import calendar #
url = 'https://invoice.etax.nat.gov.tw/index.html'
web = requests.get(url)    
web.encoding='utf-8'       

from bs4 import BeautifulSoup

class ReceiptService:
    LedgerDao = LedgerDao.LedgerDao()
    LedgerAccessDao = LedgerAccessDao.LedgerAccessDao()
    RecordDao = RecordDao.RecordDao()
    ReceiptDao = ReceiptDao.ReceiptDao()

    def add_receipt(self,record_param,receipt_param):
        receipt = self.ReceiptDao.get_receipt_by_recordID(record_param)
        if receipt != None:
            return {'status': 'fail', 'error': 'This recordID\'s receipt already exist'}
        
        record = self.RecordDao.get_record_by_id(record_param)
        if record is None:
            return {'status': 'fail', 'error': 'record does not exist'}
        
        if(len(receipt_param.StatusCode) != 8 or receipt_param.StatusCode.isnumeric()==False):
            return {'status': 'fail', 'error': 'Statuscode does not legal! Need 8 numbers.'}
        receipt_param.RecordID = record
        receipt_param.BuyDate = record.BoughtDate
        try:
            receipt = self.ReceiptDao.add_receipt(receipt_param)
        except:
            return {'status': 'fail', 'error': 'Add receipt failed'}
        return {'status': 'success', 'receipt': ReceiptSerializer(receipt).data}
    
    def delete_receipt(self,receipt_param):
        receipt = self.ReceiptDao.get_receipt_by_id(receipt_param)
        if receipt is None:
            return {'status': 'fail', 'error': 'receipt does not exist'}
        
        try:
            receipt = self.ReceiptDao.delete_receipt(receipt)
        except :
            return {'status': 'fail', 'error': 'Receipt deletion failed'}

        return {'status': 'success', 'receipt': ReceiptSerializer(receipt).data}
    
    def update_receipt_statusCode(self,receipt_param):
        receipt = self.ReceiptDao.get_receipt_by_id(receipt_param)
        if receipt is None:
            return {'status': 'fail', 'error': 'receipt does not exist'}
        
        if(len(receipt_param.StatusCode) != 8 or receipt_param.StatusCode.isnumeric()==False):
            return {'status': 'fail', 'error': 'Statuscode does not legal! Need 8 numbers.'}
        receipt.StatusCode=receipt_param.StatusCode

        try:
            receipt = self.ReceiptDao.update_receipt(receipt)
        except :
            return {'status': 'fail', 'error': 'Receipt update failed'}

        return {'status': 'success', 'receipt': ReceiptSerializer(receipt).data}

    def get_receipts(self,user_param):
        ledgers =self.LedgerAccessDao.get_all_ledger_access_by_userID(user_param)
        if(ledgers.count() == 0):
            return {'status': 'fail', 'error': 'User has no ledger','receipt':[]}
        records = self.RecordDao.get_user_records_by_ledgers(ledgers)
        if(records.count() == 0):
            return {'status': 'fail', 'error': 'User has no record','receipt':[]}
        receipts = self.ReceiptDao.get_receipts_by_records(records)
        if(receipts.count() == 0):
            return {'status': 'fail', 'error': 'User has no receipt','receipt':[]}
        return {'status': 'success', 'receipt': ReceiptSerializer(receipts, many=True).data}

    def get_receipt_by_LedgerID(self,ledger_param):
        records=self.RecordDao.get_records_by_ledger(ledger_param)
        if(records.count() == 0):
            return {'status': 'fail', 'error': 'This ledger does not has Record','receipt':[]}
        receipts = self.ReceiptDao.get_receipts_by_records(records)
        if(receipts.count() == 0):
            return {'status': 'fail', 'error': 'User has no receipt','receipt':[]}
        return {'status': 'success', 'receipt': ReceiptSerializer(receipts, many=True).data}

    def get_receipt_by_recordID(self,record_param):

        receipt = self.ReceiptDao.get_receipt_by_recordID(record_param)
        if receipt is None:
           return {'status': 'fail', 'error': 'RecordID\'s receipt does not exist'}
        return {'status': 'success', 'receipt': ReceiptSerializer(receipt).data}

    def get_receipt_win_info(self):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        nss = winlist[0].getText()  
        ns = winlist[1].getText() 
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 
        info={'issue':issue,'特別獎':nss,'特獎':ns,'頭獎':n1}
        return  {'status': 'success', 'info': info}


    def check_receipt_by_statusCode(self,receipt_param):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        nss = winlist[0].getText()  
        ns = winlist[1].getText() 
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 

        if(len(receipt_param.StatusCode) != 8 or receipt_param.StatusCode.isnumeric()==False):
            return {'status': 'fail', 'error': 'Statuscode does not legal! Need 8 numbers.'}
        inputnum = receipt_param.StatusCode
        try:
            money=self.check_receipt(inputnum,nss,ns,n1)
            return  {'status': 'success','issue':issue[0:10],'StatusCode':inputnum,'money': money}
        except:
            print("ERROR") 
            return  {'status': 'fail', 'message': 'claim_receipt Server wrong'}
    
    def check_receipt_by_LedgerID(self,ledger_param):
        records = self.RecordDao.get_records_by_ledger(ledger_param)
        if(records.count() == 0):
            return {'status': 'fail', 'error': 'This ledger does not has Record'}
        info = self.get_receipt_win_info()
        info = info['info']
        info = info['issue']
        year=int(info[0:3])+1911
        start_month=info[4:6]
        end_month=info[7:9]
        end_day=calendar.monthrange(year,int(end_month))[1]
        start = str(year)+'-'+start_month+"-01 00:00:00.000000"
        end = str(year)+'-'+end_month+"-"+str(end_day) +" 23:59:59.999999"

        receipts = self.ReceiptDao.get_receipts_by_records_and_date(records,start,end)
        if(receipts.count() == 0):
            return {'status': 'fail', 'error': 'User has no receipt in this date range'}
        result=self.check_many_win_receipt_number(receipts)
        return result


    def check_many_win_receipt_number(self,Receipts):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        nss = winlist[0].getText()  
        ns = winlist[1].getText() 
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 

        receipt_result={'Receipts':[]}
        for Receipt in Receipts:
            inputnum = Receipt.StatusCode
            try:
                money =self.check_receipt(inputnum,nss,ns,n1)
                receipt_result['Receipts'].append({'RecordID':Receipt.RecordID.RecordID,'StatusCode':inputnum,'money':money})
                
            except:
                print("ERROR") 
                return  {'status': 'fail', 'message': 'claim_receipt Server wrong'}

        return  {'status': 'success','issue':issue[0:10],'result':receipt_result}  

    def check_receipt_by_RecordID(self,record_param):
        record = self.RecordDao.get_record_by_id(record_param)
        if record is None:
            return {'status': 'fail', 'error': 'Record does not exist'}
        
        info = self.get_receipt_win_info()
        info = info['info']
        info = info['issue']
        year=int(info[0:3])+1911
        start_month=info[4:6]
        end_month=info[7:9]
        end_day=calendar.monthrange(year,int(end_month))[1]
        start = str(year)+'-'+start_month+"-01 00:00:00.000000"
        end = str(year)+'-'+end_month+"-"+str(end_day) +" 23:59:59.999999"

        receipt = self.ReceiptDao.get_receipt_by_recordID(record_param)
        if receipt is None:
            return {'status': 'fail', 'error': 'Receipt does not exist'}

        receipt = self.ReceiptDao.get_receipt_by_records_and_date(record,start,end)
        if receipt is None:
            return {'status': 'fail', 'error': 'Record\'s receipt  does not this month'}
        result=self.check_win_receipt_number(receipt)
        return result

    def check_win_receipt_number(self,Receipt):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        nss = winlist[0].getText()  
        ns = winlist[1].getText() 
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 

        inputnum = Receipt.StatusCode
        try:
            money=self.check_receipt(inputnum,nss,ns,n1)
            return  {'status': 'success','issue':issue[0:10],'RecordID': Receipt.RecordID.RecordID, 'StatusCode':inputnum,'money': money}
        except:
            print("ERROR") 
            return  {'status': 'fail', 'message': 'claim_receipt Server wrong'}
        
            
    def check_receipt(self,inputnum,nss,ns,n1):
        money="0"
        if inputnum == nss: 
            money="1000萬元"
        if inputnum == ns: 
            money="200萬"
        for i in n1:
            if inputnum == i:
                money="20萬"
                break
            if inputnum[-7:] == i[-7:]:
                money="4萬"
                break
            if inputnum[-6:] == i[-6:]:
                money="1萬"
                break
            if inputnum[-5:] == i[-5:]:
                money="4000"
                break
            if inputnum[-4:] == i[-4:]:
                money="1000"
                break
            if inputnum[-3:] == i[-3:]:
                money="200"
                break
        return money
