from apiDao import UserDao, LedgerDao, LedgerAccessDao
from apiServices.LedgerService import check_ledger_access



class LedgerAccessService:
    UserDao = UserDao.UserDao()
    LedgerDao = LedgerDao.LedgerDao()
    LedgerAccessDao = LedgerAccessDao.LedgerAccessDao()
    def __init__(self):
        pass

    @check_ledger_access(['Owner'])
    def create_ledger_access(self, requested_user_param, user_param, ledger_param, AccessLevel):
        user_param = self.UserDao.get_user_by_id(user_param.UserID)
        ledger_param = self.LedgerDao.get_ledger_by_id(ledger_param.LedgerID)
        if user_param is None:
            return {'status': 'fail', 'message': 'User not found'}
        if ledger_param is None:
            return {'status': 'fail', 'message': 'Ledger not found'}
        if self.LedgerAccessDao.get_ledger_access(user_param, ledger_param) is not None:
            return {'status': 'fail', 'message': 'Ledger access already exists'}
        result = self.LedgerAccessDao.create_ledger_access(user_param, ledger_param, AccessLevel)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger access creation failed'}
        else:
            return {'status': 'success', 'message': 'Ledger access created successfully'}

    @check_ledger_access(['Owner'])
    def update_ledger_access(self, requested_user_param, user_param, ledger_param, AccessLevel):
        user_param = self.UserDao.get_user_by_id(user_param.UserID)
        ledger_param = self.LedgerDao.get_ledger_by_id(ledger_param.LedgerID)
        if user_param is None:
            return {'status': 'fail', 'message': 'User not found'}
        if ledger_param is None:
            return {'status': 'fail', 'message': 'Ledger not found'}
        ledger_access_param = self.LedgerAccessDao.get_ledger_access(user_param, ledger_param)
        if ledger_access_param is None:
            return {'status': 'fail', 'message': 'Ledger access does not exists'}
        elif ledger_access_param.AccessLevel == 'Owner':
            return {'status': 'fail', 'message': 'Owner cannot be changed'}
        ledger_access_param.AccessLevel = AccessLevel
        result = self.LedgerAccessDao.update_ledger_access(ledger_access_param)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger access update failed'}
        else:
            return {'status': 'success', 'message': 'Ledger access created successfully'}

    @check_ledger_access(['Owner'])
    def delete_ledger_access(self, requested_user_param, user_param, ledger_param):
        user_param = self.UserDao.get_user_by_id(user_param.UserID)
        ledger_param = self.LedgerDao.get_ledger_by_id(ledger_param.LedgerID)
        if user_param is None:
            return {'status': 'fail', 'message': 'User not found'}
        if ledger_param is None:
            return {'status': 'fail', 'message': 'Ledger not found'}
        ledger_access_param = self.LedgerAccessDao.get_ledger_access(user_param, ledger_param)
        if ledger_access_param is None:
            return {'status': 'fail', 'message': 'Ledger access does not exists'}
        elif ledger_access_param.AccessLevel == 'Owner':
            return {'status': 'fail', 'message': 'Owner cannot be deleted'}
        result = self.LedgerAccessDao.delete_ledger_access(ledger_access_param)
        if result is None:
            return {'status': 'fail', 'message': 'Ledger access deletion failed'}
        else:
            return {'status': 'success', 'message': 'Ledger access deleted successfully'}