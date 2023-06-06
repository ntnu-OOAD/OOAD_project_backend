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
    # 檢查使用者是否有權限存取該帳本
    # 使用者部分優先使用 requested_user_param，若無則使用 user_param

    def check_ledger_access(AccessLevel=[]):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self_ = args[0]
                user = None
                ledger = None
                if 'user_param' in kwargs:
                    user = kwargs['user_param']
                if 'requested_user_param' in kwargs:
                    user = kwargs['requested_user_param']
                if 'ledger_param' in kwargs:
                    ledger = kwargs['ledger_param']
                if 'record_param' in kwargs:
                    record = kwargs['record_param']
                    ledger = record.LedgerID
                user_access = LedgerAccessDao.LedgerAccessDao.get_ledger_access(user, ledger)
                if user_access is None or user_access.AccessLevel not in AccessLevel:
                    return {'status': 'fail', 'message': f'You have no access to this ledger method, only {", ".join([str(i) for i in AccessLevel])} can access this ledger'}
                else:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def create_ledger(self, user_param, ledger_param):
        user = self.UserDao.get_user_by_id(user_param.UserID)
        if user is None:
            return {'status': 'fail', 'message': 'User not found', 'ledger': None}
        ledger_param.OwnerID = user
        with transaction.atomic():
            ledger = self.LedgerDao.create_ledger(user_param, ledger_param)
            ledger_access = self.LedgerAccessDao.create_ledger_access(user_param, ledger, 'Owner')
        if ledger is None or ledger_access is None:
            return {'status': 'fail', 'message': 'Ledger creation failed', 'ledger': None}
        else:
            return {'status': 'success', 'message': 'Ledger created successfully', 'ledger': LedgerSerializer(ledger).data}

    def get_ledgers(self, user_param):
        result = self.LedgerDao.get_all_ledgers(user_param)
        return {'status': 'success', 'message': 'Ledger list retrieved successfully', 'ledger_with_access': result}

    @check_ledger_access(AccessLevel=['Viewer', 'Editor', 'Owner'])
    def get_ledger_info(self, user_param, ledger_param, with_access_level=False):
        result = self.LedgerDao.get_ledger_info(ledger_param, with_access_level=with_access_level)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger not found', 'ledger_with_access': None}
        else:
            return {'status': 'success', 'message': 'Ledger found', 'ledger_with_access': result}

    @check_ledger_access(AccessLevel=['Owner', 'Editor'])
    def update_ledger(self, user_param, ledger_param):
        ledger = self.LedgerDao.get_ledger_by_id(ledger_param)
        if ledger is None:
            return {'status': 'fail', 'message': 'Ledger not found', 'ledger': None}
        ledger.LedgerName = ledger_param.LedgerName
        result = self.LedgerDao.update_ledger(ledger)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger update failed', 'ledger': None}
        else:
            return {'status': 'success', 'message': 'Ledger updated successfully', 'ledger': LedgerSerializer(result).data}

    @check_ledger_access(AccessLevel=['Owner'])
    def delete_ledger(self, user_param, ledger_param):
        ledger = self.LedgerDao.get_ledger_by_id(ledger_param)
        if ledger is None:
            return {'status': 'fail', 'message': 'Ledger not found', 'ledger': None}
        result = self.LedgerDao.delete_ledger(ledger)
        if result is None or False:
            return {'status': 'fail', 'message': 'Ledger deletion failed', 'ledger': None}
        else:
            return {'status': 'success', 'message': 'Ledger deleted successfully', 'ledger': None}
