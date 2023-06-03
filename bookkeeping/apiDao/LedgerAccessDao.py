from api.models import *

class LedgerAccessDao:
    @staticmethod
    def create_ledger_access(user_param, ledger_param, AccessLevel):
        try:
            ledger_access = LedgerAccess.objects.create(
                UserID=user_param, 
                LedgerID=ledger_param, 
                AccessLevel=AccessLevel)
            ledger_access.save()
            return ledger_access
        except:
            return None
    @staticmethod
    def update_ledger_access(ledger_access_param):
        try:
            ledger_access_param.save()
            return ledger_access_param
        except:
            return None
    @staticmethod
    def delete_ledger_access(ledger_access_param):
        try:
            ledger_access_param.delete()
            return True
        except:
            return None

    @staticmethod
    def get_ledger_access(user_param, ledger_param):
        ledger_access = LedgerAccess.objects.filter(
            UserID=user_param, 
            LedgerID=ledger_param).first()
        return ledger_access
    
    @staticmethod
    def get_all_ledger_access_by_userID(user_param):
        ledger_access = LedgerAccess.objects.filter(
            UserID=user_param)
        return ledger_access