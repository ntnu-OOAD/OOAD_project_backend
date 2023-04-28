from .models import *
from rest_framework import viewsets,permissions
from .serializer import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password    
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg import openapi
from django.db import connection
from django.db.models import Q, F

# from bookkeeping_services import user_services
# user_services.printHello()

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser,FormParser, JSONParser)
    
    @swagger_auto_schema(operation_summary='登入',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'UserName': openapi.Schema(type=openapi.TYPE_STRING, description='使用者名稱'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密碼'),
            },),)
    @action(detail=False, methods=['post'] )
    def login(self, request):
        UserName = request.data['UserName']
        password = request.data['password']
        user = authenticate(UserName=UserName, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail'})

    @swagger_auto_schema(operation_summary='登出',
        request_body=None
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        logout(request)
        return JsonResponse({'status': 'success'})

    @swagger_auto_schema(operation_summary='註冊',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'UserName': openapi.Schema(type=openapi.TYPE_STRING, description='使用者名稱'),
                'UserNickname': openapi.Schema(type=openapi.TYPE_STRING, description='使用者暱稱'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密碼'),
            },),)
    @action(detail=False, methods=['post'])
    def register(self, request):
        UserName = request.data['UserName']
        UserNickname = request.data['UserNickname']
        password = request.data['password']
        # check if UserID is already taken
        if User.objects.filter(UserName=UserName).exists():
            return JsonResponse({'status': 'fail', 'error': 'UserName already taken'})
        user = User.objects.create_user(UserName=UserName, UserNickname=UserNickname, password=password)
        user.save()
        return JsonResponse({'status': 'success'})

    @swagger_auto_schema(operation_summary='修改密碼',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='舊密碼'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密碼'),
            },),)
    @action(detail=False, methods=['put'])
    def change_password(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        user = User.objects.get(UserID=request.user.UserID)
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail', 'error': 'incorrect old password'})
    
    @swagger_auto_schema(operation_summary='修改使用者資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'UserNickname': openapi.Schema(type=openapi.TYPE_STRING, description='使用者暱稱'),
            },),)
    @action(detail=False, methods=['put'])
    def change_user_info(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        user = User.objects.get(UserID=request.user.UserID)
        if 'UserNickname' in request.data:
            user.UserNickname = request.data['UserNickname']
        user.save()
        return JsonResponse({'status': 'success'})
    @swagger_auto_schema(operation_summary='取得使用者資料',
        request_body=None
    )
    @action(detail=False, methods=['get'])
    def get_user(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        user = User.objects.get(UserID=request.user.UserID)
        return JsonResponse({'status': 'success', 'user': UserSerializer(user).data})
    
    @swagger_auto_schema(
        operation_summary='根據 UserName 取得 UserID',
        manual_parameters=[
            openapi.Parameter('UserName', openapi.IN_QUERY, description="User Name", type=openapi.TYPE_STRING),
        ],
        )
    @action(detail=False, methods=['get'])
    def get_userid_from_username(self, request):
        UserName = request.GET.get('UserName')
        user = User.objects.get(UserName=UserName)
        return JsonResponse({'status': 'success', 'UserID': user.UserID})


class LedgerViewSet(viewsets.GenericViewSet):
    queryset = Ledger.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = LedgerSerializer

    @swagger_auto_schema(operation_summary='建立帳本',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerName': openapi.Schema(type=openapi.TYPE_STRING, description='帳本名稱'),
                'LedgerType': openapi.Schema(type=openapi.TYPE_STRING, description='帳本類型'),
            },),)
    @action(detail=False, methods=['post'])
    def create_ledger(self, request):
        LedgerName = request.data['LedgerName']
        LedgerType = request.data['LedgerType']
        OwnerID = request.user.UserID
        user = User.objects.get(UserID=OwnerID)
        ledger = Ledger.objects.create( OwnerID=user, LedgerName=LedgerName, LedgerType=LedgerType)
        ledger.save()
        ledger_access = LedgerAccess.objects.create(LedgerID=ledger, UserID=user, AccessLevel="Owner")
        ledger_access.save()
        return JsonResponse({'status': 'success', 'ledger': LedgerSerializer(ledger).data})
    
    @swagger_auto_schema(operation_summary='取得有觀看權限的帳本資料',
        request_body=None
    )
    @action(detail=False, methods=['get'])
    def get_ledgers(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        ledger_with_access = Ledger.objects.filter(
            Q(ledgeraccess__UserID_id=request.user.UserID)).values(
                'LedgerID', 'LedgerName', 'LedgerType', 'OwnerID', AccessLevel=F('ledgeraccess__AccessLevel'))
        return JsonResponse({'status': 'success', 'ledger_with_access': list(ledger_with_access)})

    @swagger_auto_schema(operation_summary='取得單一帳本詳細資料及有權限的使用者資料(optional)',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
            openapi.Parameter('with_access_level', openapi.IN_QUERY, description="是否要取得有權限的使用者資料", type=openapi.TYPE_BOOLEAN),
        ],
        )
    @action(detail=False, methods=['get'])
    def get_ledger_info(self, request):
        LedgerID = request.GET.get('LedgerID')
        ledger = Ledger.objects.get(LedgerID=LedgerID)
        if (request.GET.get('with_access_level') != 'true'):
            return JsonResponse({'status': 'success', 'ledger': LedgerSerializer(ledger).data})
        # filter ledger access level for this ledger and join with user table
        users_access_list = LedgerAccess.objects.filter(LedgerID=ledger
            ).values(
                'UserID', 'AccessLevel', UserName=F('UserID__UserName'), UserNickname=F('UserID__UserNickname'))
        ledger_with_access = {
            "ledger": LedgerSerializer(ledger).data,
            "users_access_list": list(users_access_list)
        }
        return JsonResponse({'status': 'success', 'ledger_with_access': ledger_with_access  })

    @swagger_auto_schema(operation_summary='修改帳本資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='要修改的帳本ID'),
                'LedgerName': openapi.Schema(type=openapi.TYPE_STRING, description='帳本名稱'),
                'LedgerType': openapi.Schema(type=openapi.TYPE_STRING, description='帳本類型'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_ledger(self, request):
        LedgerID = request.data['LedgerID']
        ledger = Ledger.objects.get(LedgerID=LedgerID)
        # check if user have Owner access level to the ledger
        if(ledger.ledgeraccess_set.filter(UserID=request.user.UserID, AccessLevel="Owner").exists() == False):
            return JsonResponse({'status': 'fail', 'error': 'user have no access to the ledger'})
        if 'LedgerName' in request.data:
            ledger.LedgerName = request.data['LedgerName']
        if 'LedgerType' in request.data:
            ledger.LedgerType = request.data['LedgerType']
        ledger.save()
        return JsonResponse({'status': 'success', 'ledger': LedgerSerializer(ledger).data})


class LedgerAccessViewSet(viewsets.GenericViewSet):
    queryset = LedgerAccess.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = LedgerAccessSerializer
    @action(detail=False, methods=['post'])
    def create_ledger_access(self, request):
        LedgerID = request.data['LedgerID']
        ledger = Ledger.objects.get(LedgerID=LedgerID)
        UserID = request.data['UserID']
        user = User.objects.get(UserID=UserID)
        AccessLevel = request.data['AccessLevel']
        # check if user have Owner or Coll access level to the ledger
        if(ledger.ledgeraccess_set.filter(UserID=request.user.UserID, AccessLevel__in=["Owner", "Coll"]).exists() == False):
            return JsonResponse({'status': 'fail', 'error': 'user have no access to the ledger'})
        # check if user or ledger does not exist
        if(ledger is None or user is None):
            return JsonResponse({'status': 'fail', 'error': 'user or ledger does not exist'})
        ledger_access = LedgerAccess.objects.create(LedgerID=ledger, UserID=user, AccessLevel=AccessLevel)
        ledger_access.save()
        return JsonResponse({'status': 'success', 'ledger_access': LedgerAccessSerializer(ledger_access).data})



class RecordViewSet(viewsets.GenericViewSet):
    queryset = Record.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = RecordSerializer

    @swagger_auto_schema(operation_summary='新增紀錄資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='要新增紀錄之帳本ID'),
                'ItemName': openapi.Schema(type=openapi.TYPE_STRING, description='物品名稱'),
                'ItemType': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型'),
                'Cost': openapi.Schema(type=openapi.TYPE_STRING, description='價錢'),
                'Payby': openapi.Schema(type=openapi.TYPE_STRING, description='付錢者UserID'),
                'BoughtDate': openapi.Schema(type=openapi.TYPE_STRING, description='購買日期'),
            },),)    
    @action(detail=False, methods=['post'])
    def create_record(self, request):
        LedgerID = request.data['LedgerID']
        ItemName = request.data['ItemName']
        ItemType = request.data['ItemType']
        Cost = request.data['Cost']
        Payby = request.data['Payby']
        BoughtDate = request.data['BoughtDate']
        if(BoughtDate == ''):
            BoughtDate = datetime.now()
        ledger = Ledger.objects.get(LedgerID=LedgerID)
        payby = User.objects.get(UserID=Payby)
        record = Record.objects.create(LedgerID=ledger, ItemName=ItemName, ItemType=ItemType, Cost=Cost, Payby=payby, BoughtDate=BoughtDate)
        record.save()
        return JsonResponse({'status': 'success', 'record': RecordSerializer(record).data})
    
    # get records by ledger with ledgerID as parameter
    @swagger_auto_schema(operation_summary='取得紀錄所屬帳本',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='紀錄的ID'),
            },),)    
    @action(detail=False, methods=['post'])
    def get_records_by_ledger(self, request):
        RecordID = request.data['RecordID']
        LedgerID = request.GET.get('LedgerID')
        records = Record.objects.filter(LedgerID=LedgerID)
        return JsonResponse({'status': 'success', 'records': RecordSerializer(records, many=True).data})