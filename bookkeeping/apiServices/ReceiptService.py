from api.models import *
from django.db import transaction
from api.serializer import *

import requests
url = 'https://invoice.etax.nat.gov.tw/index.html'
web = requests.get(url)    
web.encoding='utf-8'       

from bs4 import BeautifulSoup

class ReceiptService:
    def get_receipt_win_info(self):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        #特別獎
        nss = winlist[0].getText()  
        #特獎
        ns = winlist[1].getText() 
        # 頭獎
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 
        info={'issue':issue,'特別獎':nss,'特獎':ns,'頭獎':n1}
        return  {'status': 'success', 'info': info}


    def check_win_receipt_number(self,StatusCode):
        tree = BeautifulSoup(web.text, "html.parser")  
        issue = tree.select(".carousel-item")[0].getText(); 
        winlist = tree.select('.container-fluid')[0].select('.etw-tbiggest')  
        nss = winlist[0].getText()  
        ns = winlist[1].getText() 
        n1 = [winlist[2].getText()[-8:], winlist[3].getText()[-8:], winlist[4].getText()[-8:]] 

        inputnum = StatusCode
        money="0"
        try:
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
            return  {'status': 'success', 'StatusCode':StatusCode,'money': money}
        except:
            print("ERROR") 
            return  {'status': 'fail', 'message': 'claim_receipt Server wrong'}
        
        
            
