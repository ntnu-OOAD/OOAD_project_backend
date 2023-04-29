from apiDao import UserDao
from django.contrib.auth import authenticate, login, logout
from api.serializer import UserSerializer

class UserService:
    Dao = UserDao.UserDao()
    @staticmethod
    def login(request, user_param):
        user = authenticate(username=user_param.UserName, password=user_param.password)
        if user:
            login(request, user)
            return {'status': 'success', 'message': 'Login successfully.'}
        else:
            return {'status': 'fail', 'message': 'Username or password is incorrect.'}
    @staticmethod
    def logout(request):
        result = logout(request)
        if result:
            return {'status': 'success', 'message': 'Logout successfully.'}
        else:
            return {'status': 'fail', 'message': 'Logout failed.'}
    
    def register(self, user_param):
        if(self.Dao.get_userid_by_username(user_param.UserName)):
            return {'status': 'fail', 'message': 'UserName already exists.'}
        result = self.Dao.create_user(user_param)
        if result:
            return {'status': 'success', 'message': 'Register successfully.'}
        else:
            return {'status': 'fail', 'message': 'Register failed.'}
    
    def change_password(self, user_param, old_password, new_password):
        user = authenticate(username=user_param.UserName, password=old_password)
        if user == None:
            return {'status': 'fail', 'message': 'Incorrect old password.'}
        result = self.Dao.change_password(user, new_password)
        if result:
            return {'status': 'success', 'message': 'Change password successfully.'}
        else:
            return {'status': 'fail', 'message': 'Change password failed.'}

    def change_user_info(self, user_param):
        result = self.Dao.change_user_info(user_param)
        if result:
            return {'status': 'success', 'message': 'Change user info successfully.'}
        else:
            return {'status': 'fail', 'message': 'Change user info failed.'}
    
    def get_user_by_id(self, user_param):
        result = self.Dao.get_user_by_id(user_param.UserID)
        if result:
            return {'status': 'success', 'message': 'Get user successfully.', 'user': UserSerializer(result).data}
        else:
            return {'status': 'fail', 'message': 'Get user failed.'}
    
    def get_userid_by_username(self, user_param):
        result = self.Dao.get_userid_by_username(user_param.UserName)
        if result:
            return {'status': 'success', 'message': 'Get user successfully.', 'UserID': result.UserID}
        else:
            return {'status': 'fail', 'message': 'Get userid failed.'}