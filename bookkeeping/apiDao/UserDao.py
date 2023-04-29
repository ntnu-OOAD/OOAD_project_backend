from api.models import User

class UserDao:
    @staticmethod
    def create_user(user_param):
        user = User.objects.create_user(UserName=user_param.UserName, UserNickname=user_param.UserNickname, password=user_param.password)
        try:
            user.save()
            return user
        except:
            return None
    @staticmethod
    def change_password(user_param , new_password):
        user = user_param
        user.set_password(new_password)
        try:
            user.save()
            return user
        except:
            return None

    @staticmethod
    def change_user_info(user_param):
        user = user_param
        try:
            user.save()
            return user
        except:
            return None

    @staticmethod
    def get_user_by_id(UserID=None):
        return User.objects.filter(UserID=UserID).first()

    @staticmethod
    def get_userid_by_username(UserName=None):
        return User.objects.filter(UserName=UserName).first()
    