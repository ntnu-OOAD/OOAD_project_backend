from api.models import *
from apiDao import UserDao, LedgerDao, LedgerAccessDao
from django.db import transaction
from api.serializer import *
from functools import wraps

class LedgerService:
    UserDao = UserDao.UserDao()
    LedgerDao = LedgerDao.LedgerDao()
    LedgerAccessDao = LedgerAccessDao.LedgerAccessDao()
    def __init__(self):
        pass
    
    # Decorator for checking ledger access
    @staticmethod
    def check_ledger_access(AccessLevel=[]):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self_ = args[0]
                user = None
                ledger = None
                if 'user_param' in kwargs:
                    user = kwargs['user_param']
                if 'ledger_param' in kwargs:
                    ledger = kwargs['ledger_param']
                if 'record_param' in kwargs:
                    record = kwargs['record_param']
                    ledger = record.LedgerID
                user_access = LedgerAccess.objects.filter(UserID=user, LedgerID=ledger).first()
                if user_access is None or user_access.AccessLevel not in AccessLevel:
                    return {'status': 'fail', 'message': f'You have no access to this ledger method, only {", ".join([str(i) for i in AccessLevel])} can access this ledger'}
                else:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    


    def create_ledger(self, user_param, ledger_param):
        user = self.UserDao.get_user_by_id(user_param.UserID)
        if user is None:
            return {'status': 'fail', 'message': 'User not found'}
        ledger_param.OwnerID = user
        with transaction.atomic():
            ledger = self.LedgerDao.create_ledger(user_param, ledger_param)
            ledger_access = self.LedgerAccessDao.create_ledger_access(user_param, ledger, 'Owner')
        if ledger is None or ledger_access is None:
            return {'status': 'fail', 'message': 'Ledger creation failed'}
        else:
            return {'status': 'success', 'message': 'Ledger created successfully'}

    def get_ledgers(self, user_param):
        result = self.LedgerDao.get_all_ledgers(user_param)
        return {'status': 'success', 'message': 'Ledger list retrieved successfully', 'data': result}

    @check_ledger_access(AccessLevel=['Viewer', 'Editor', 'Owner'])
    def get_ledger_info(self, user_param, ledger_param, with_access_level=False):
        result = self.LedgerDao.get_ledger_info(ledger_param, with_access_level=with_access_level)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger not found'}
        else:
            return {'status': 'success', 'ledger_with_access': result}

    @check_ledger_access(AccessLevel=['Viewer', 'Editor'])
    def update_ledger(self, user_param, ledger_param):
        ledger_info = self.LedgerDao.get_ledger_info(ledger_param)
        if ledger_info is None:
            return {'status': 'fail', 'message': 'Ledger not found'}
        ledger = ledger_info['ledger']
        ledger.LedgerName = ledger_param.LedgerName
        result = self.LedgerDao.update_ledger(ledger)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger update failed'}
        else:
            return {'status': 'success', 'message': 'Ledger updated successfully'}