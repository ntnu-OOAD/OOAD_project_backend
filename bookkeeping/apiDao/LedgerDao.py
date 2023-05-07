from api.models import *
from api.serializer import *
from django.db.models import Q, F

class LedgerDao:
    @staticmethod
    def create_ledger(user_param, ledger_param):
        try:
            ledger = Ledger.objects.create(
                OwnerID=user_param, 
                LedgerName=ledger_param.LedgerName, 
                LedgerType=ledger_param.LedgerType,)
            ledger.save()
            return ledger
        except:
            return None
           
    @staticmethod
    def get_all_ledgers(user_param):
        ledger_with_access = Ledger.objects.filter(
            Q(ledgeraccess__UserID_id=user_param.UserID)).values(
                'LedgerID', 'LedgerName', 'LedgerType', 'OwnerID', AccessLevel=F('ledgeraccess__AccessLevel'))
        return list(ledger_with_access)
    
    @staticmethod
    def get_ledger_by_id(ledger_param):
        ledger = Ledger.objects.filter(LedgerID=ledger_param.LedgerID).first()
        return ledger

    @staticmethod
    def get_ledger_info(ledger_param, with_access_level=False):
        ledger = Ledger.objects.filter(LedgerID=ledger_param.LedgerID).first()
        if ledger is None:
            return None
        users_access_list = []
        if with_access_level:
            users_access_list = LedgerAccess.objects.filter(LedgerID=ledger
            ).values(
                'UserID', 'AccessLevel', UserName=F('UserID__UserName'), UserNickname=F('UserID__UserNickname'))
        ledger_with_access = {
            "ledger": LedgerSerializer(ledger).data,
            "users_access_list": list(users_access_list)
        }
        return ledger_with_access
    @staticmethod
    def update_ledger(ledger_param):
        try:
            ledger_param.save()
            return ledger_param
        except:
            return None
    @staticmethod
    def delete_ledger(ledger_param):
        try:
            ledger_param.delete()
            return True
        except:
            return False