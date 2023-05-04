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