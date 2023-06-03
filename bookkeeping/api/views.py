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

from apiServices import UserService, LedgerService, LedgerAccessService,RecordService,ReceiptService,SharePayService

class UserViewSet(viewsets.GenericViewSet):
    service = UserService.UserService()
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
        user_param = User(
            UserName=request.data.get('UserName'), 
            password=request.data.get('password'))
        result = self.service.login(request, user_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='登出',
        request_body=None
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        result = self.service.logout(request)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='註冊',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'UserName': openapi.Schema(type=openapi.TYPE_STRING, description='使用者名稱'),
                'UserNickname': openapi.Schema(type=openapi.TYPE_STRING, description='使用者暱稱'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密碼'),
            },),)
    @action(detail=False, methods=['post'])
    def register(self, request):
        user_param = User(
            UserName=request.data.get('UserName'), 
            UserNickname=request.data.get('UserNickname'),
            password=request.data.get('password')
        )
        result = self.service.register(user_param)
        return JsonResponse(result)
        
    @swagger_auto_schema(operation_summary='修改密碼',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='舊密碼'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密碼'),
            },),)
    @action(detail=False, methods=['put'])
    def change_password(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user_param = request.user
        result = self.service.change_password(user_param, old_password, new_password)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='修改使用者資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'UserNickname': openapi.Schema(type=openapi.TYPE_STRING, description='使用者暱稱'),
            },),)
    @action(detail=False, methods=['put'])
    def change_user_info(self, request):
        user_param = request.user
        user_param.UserNickname = request.data.get('UserNickname')
        result = self.service.change_user_info(user_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='取得使用者資料',
        request_body=None
    )
    @action(detail=False, methods=['get'])
    def get_user(self, request):
        user_param = request.user
        result = self.service.get_user_by_id(user_param)
        return JsonResponse(result)

    @swagger_auto_schema(
        operation_summary='根據 UserName 取得 UserID',
        manual_parameters=[
            openapi.Parameter('UserName', openapi.IN_QUERY, description="User Name", type=openapi.TYPE_STRING),
        ],
        )
    @action(detail=False, methods=['get'])
    def get_user_from_username(self, request):
        user_param = User(
            UserName=request.GET.get('UserName'))
        result = self.service.get_userid_by_username(user_param)
        return JsonResponse(result)
        
class LedgerViewSet(viewsets.GenericViewSet):
    service = LedgerService.LedgerService()
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
        user_param = User(
            UserID = request.user.UserID
        )
        ledger_param = Ledger(
            LedgerName=request.data.get('LedgerName'), 
            LedgerType=request.data.get('LedgerType')
        )
        result = self.service.create_ledger(user_param, ledger_param)
        return JsonResponse(result)
        
    @swagger_auto_schema(operation_summary='取得有觀看權限的帳本資料',
        request_body=None
    )
    @action(detail=False, methods=['get'])
    def get_ledgers(self, request):
        user = request.user
        result = self.service.get_ledgers(user)
        return JsonResponse(result)
        
    @swagger_auto_schema(operation_summary='取得單一帳本詳細資料及有權限的使用者資料(optional)',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
            openapi.Parameter('with_access_level', openapi.IN_QUERY, description="是否要取得有權限的使用者資料", type=openapi.TYPE_BOOLEAN),
        ],
        )
    @action(detail=False, methods=['get'])
    def get_ledger_info(self, request):
        ledger_param = Ledger(
            LedgerID = request.GET.get('LedgerID')
        )
        user_param = request.user
        with_access_level = request.GET.get('with_access_level')
        result = self.service.get_ledger_info(user_param=user_param, ledger_param=ledger_param, with_access_level=with_access_level)
        return JsonResponse(result)

        
    @swagger_auto_schema(operation_summary='修改帳本資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_INTEGER, description='要修改的帳本ID'),
                'LedgerName': openapi.Schema(type=openapi.TYPE_STRING, description='帳本名稱'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_ledger(self, request):
        LedgerID = request.data['LedgerID']
        ledger = Ledger(
            LedgerID=LedgerID, 
            LedgerName=request.data.get('LedgerName'),
        )
        result = self.service.update_ledger(user_param=request.user, ledger_param=ledger)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='刪除帳本',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_INTEGER, description='要刪除的帳本ID'),
            },),)
    @action(detail=False, methods=['post'])
    def delete_ledger(self, request):
        ledger = Ledger(
            LedgerID=request.data.get('LedgerID')
        )
        result = self.service.delete_ledger(user_param=request.user, ledger_param=ledger)
        return JsonResponse(result)
        

class LedgerAccessViewSet(viewsets.GenericViewSet):
    queryset = LedgerAccess.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    service = LedgerAccessService.LedgerAccessService()
    serializer_class = LedgerAccessSerializer
    @swagger_auto_schema(operation_summary='新增帳本權限',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='帳本ID'),
                'UserID': openapi.Schema(type=openapi.TYPE_STRING, description='使用者ID'),
                'AccessLevel': openapi.Schema(type=openapi.TYPE_STRING, description='權限等級'),
            },),)
    @action(detail=False, methods=['post'])
    def create_ledger_access(self, request):
        ledger_param = Ledger(LedgerID = request.data.get('LedgerID'))
        user_param = User(UserID = request.data.get('UserID'))
        requested_user_param = request.user
        AccessLevel = request.data.get('AccessLevel')
        result = self.service.create_ledger_access(
            requested_user_param=requested_user_param, ledger_param=ledger_param, 
            user_param=user_param, AccessLevel=AccessLevel)
        return JsonResponse(result)
    
    @swagger_auto_schema(operation_summary='修改帳本權限',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='帳本ID'),
                'UserID': openapi.Schema(type=openapi.TYPE_STRING, description='使用者ID'),
                'AccessLevel': openapi.Schema(type=openapi.TYPE_STRING, description='權限等級'),
            },),)
    @action(detail=False, methods=['post'])
    def update_ledger_access(self, request):
        ledger_param = Ledger(LedgerID = request.data.get('LedgerID'))
        user_param = User(UserID = request.data.get('UserID'))
        requested_user_param = request.user
        AccessLevel = request.data.get('AccessLevel')
        result = self.service.update_ledger_access(
            requested_user_param=requested_user_param, ledger_param=ledger_param, 
            user_param=user_param, AccessLevel=AccessLevel)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='刪除帳本權限',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='帳本ID'),
                'UserID': openapi.Schema(type=openapi.TYPE_STRING, description='使用者ID'),
            },),)
    @action(detail=False, methods=['post'])
    def delete_ledger_access(self, request):
        ledger_param = Ledger(LedgerID = request.data.get('LedgerID'))
        user_param = User(UserID = request.data.get('UserID'))
        requested_user_param = request.user
        result = self.service.delete_ledger_access(
            requested_user_param=requested_user_param, ledger_param=ledger_param, 
            user_param=user_param)
        return JsonResponse(result)

class RecordViewSet(viewsets.GenericViewSet):
    queryset = Record.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    service = RecordService.RecordService()
    serializer_class = RecordSerializer
    @swagger_auto_schema(operation_summary='新增分帳紀錄',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='要新增紀錄之帳本ID'),
                'ItemName': openapi.Schema(type=openapi.TYPE_STRING, description='物品名稱'),
                'ItemType': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型（食,衣,住,行,育,樂,其他/收入）'),
                'Cost': openapi.Schema(type=openapi.TYPE_STRING, description='費用(皆輸入正數)'),
                'Payby': openapi.Schema(type=openapi.TYPE_STRING, description='付錢者UserID(若空,則為create record者)'),
                'BoughtDate': openapi.Schema(type=openapi.TYPE_STRING, description='購買日期'),
                'ShareUsers': openapi.Schema(type=openapi.TYPE_ARRAY
                    ,items=openapi.Items(type=openapi.TYPE_STRING), description='分帳者們'),
            },),)    
    @action(detail=False, methods=['post'])
    def create_sharepay_record(self, request):
        user_param = User(
            UserID = request.user.UserID
        )
        record_param = Record(
            ItemName = request.data.get('ItemName'),
            ItemType = request.data.get('ItemType'),
            Cost = request.data.get('Cost'),
            BoughtDate = request.data.get('BoughtDate')
        )
        ledger_param = Ledger(
            LedgerID = request.data.get('LedgerID')
        )
        user_payby_param=User(
            UserID = request.data.get('Payby')
        )
        array_shareUsers = request.data.get('ShareUsers')
        result = self.service.create_sharepay_record(user_param,record_param,ledger_param,user_payby_param,array_shareUsers)   
        return JsonResponse(result)
  
    @swagger_auto_schema(operation_summary='刪除紀錄',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='要刪除的RecordID'),
            },),)    
    @action(detail=False, methods=['post'])
    def delete_record(self, request):
        record_param = Record(
            RecordID = request.data.get('RecordID')
        )
        result = self.service.delete_record(record_param)
        return JsonResponse(result)
    
    #update_record
    @swagger_auto_schema(operation_summary='修改紀錄資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='要修改的紀錄ID'),
                'ItemName': openapi.Schema(type=openapi.TYPE_STRING, description='物品名稱'),
                'ItemType': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型（食,衣,住,行,育,樂,其他/收入）'),
                'Cost': openapi.Schema(type=openapi.TYPE_STRING, description='費用'),
                'Payby': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型'),
                'BoughtDate': openapi.Schema(type=openapi.TYPE_STRING, description='購買物品時間'),
                'ShareUsers': openapi.Schema(type=openapi.TYPE_ARRAY
                    ,items=openapi.Items(type=openapi.TYPE_STRING), description='分帳者們'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_record(self, request):
        record_param = Record(
            RecordID = request.data.get('RecordID'),
            ItemName = request.data.get('ItemName'),
            ItemType = request.data.get('ItemType'),
            Cost = request.data.get('Cost'),
            BoughtDate = request.data.get('BoughtDate')
        )
        user_payby_param=User(
            UserID = request.data.get('Payby')
        )
        array_shareUsers = request.data.get('ShareUsers')
        result = self.service.update_record(record_param , user_payby_param , array_shareUsers)   
        return JsonResponse(result)

    # get records by ledger with ledgerID as parameter
    @swagger_auto_schema(operation_summary='取得單一帳本所有紀錄',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_records_by_ledger(self, request):
        ledger_param = Ledger(
            LedgerID = request.GET.get('LedgerID')
        )
        result = self.service.get_records_by_ledger(ledger_param)
        return JsonResponse(result)
    
    @swagger_auto_schema(operation_summary='取得當月支出類型ItemType(食,衣,住,行,育,樂,其他/收入)',
       manual_parameters=[
            openapi.Parameter('ItemType', openapi.IN_QUERY, description="ItemType", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_this_month_ItemType_cost(self, request):
        user_param = User(
            UserID = request.user.UserID
        )
        record_param = Record(
            ItemType = request.GET.get('ItemType')
        )
        result = self.service.get_this_month_ItemType_cost(user_param,record_param)

        return JsonResponse(result)
        
    @swagger_auto_schema(operation_summary='取得當月總支出',
        request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_this_month_total_pay(self, request):
        user_param = User(
            UserID = request.user.UserID
        )
        result=self.service.get_this_month_total_pay(user_param)
        return JsonResponse(result)

class ReceiptViewSet(viewsets.GenericViewSet):
    service = ReceiptService.ReceiptService()
    queryset = Receipt.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ReceiptSerializer
    @swagger_auto_schema(operation_summary='新增發票',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='新增發票之所屬紀錄ID'),
                'StatusCode': openapi.Schema(type=openapi.TYPE_STRING, description='發票號碼(8位數字)'),
            },),)    
    @action(detail=False, methods=['post'])
    def add_receipt(self, request):
        record_param = Record(
            RecordID = request.data.get('RecordID'),
        )
        receipt_param = Receipt(
            StatusCode = request.data.get('StatusCode'),
        )
        result=self.service.add_receipt(record_param,receipt_param)
        return JsonResponse(result)


    @swagger_auto_schema(operation_summary='刪除發票',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'ReceiptID': openapi.Schema(type=openapi.TYPE_STRING, description='要刪除的ReceiptID'),
            },),)    
    @action(detail=False, methods=['post'])
    def delete_receipt(self, request):
        receipt_param = Receipt(
            ReceiptID = request.data.get('ReceiptID'),
        )
        result=self.service.delete_receipt(receipt_param)
        return JsonResponse(result)
    

    @swagger_auto_schema(operation_summary='修改發票號碼',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'ReceiptID': openapi.Schema(type=openapi.TYPE_STRING, description='要修改的發票ID'),
                'StatusCode': openapi.Schema(type=openapi.TYPE_STRING, description='發票號碼(8位數字)'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_receipt_statusCode(self, request):
        receipt_param = Receipt(
            ReceiptID = request.data.get('ReceiptID'),
            StatusCode = request.data.get('StatusCode')
        )
        result=self.service.update_receipt_statusCode(receipt_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='取得使用者自己（有觀看權限）的所有發票',
         request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_receipts(self, request):
        user_param = User(
            UserID = request.user.UserID
        )
        result=self.service.get_receipts(user_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='取得帳本之所有發票',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_receipt_by_LedgerID(self, request):
        ledger_param = Ledger(
            LedgerID = request.GET.get('LedgerID')
        )
        result=self.service.get_receipt_by_LedgerID(ledger_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='取得紀錄之發票',
        manual_parameters=[
            openapi.Parameter('RecordID', openapi.IN_QUERY, description="Record ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_receipt_by_recordID(self, request):
        record_param = Record(
            RecordID = request.GET.get('RecordID'),
        )
        result=self.service.get_receipt_by_recordID(record_param)
        return JsonResponse(result)
    
    @swagger_auto_schema(operation_summary='取得近一期發票中獎號碼',
        request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_receipt_win_info(self, request):
        result = self.service.get_receipt_win_info()
        return JsonResponse(result)
        
    @swagger_auto_schema(operation_summary='發票兌獎(最近一期)By statusCode', 
        manual_parameters=[
            openapi.Parameter('StatusCode', openapi.IN_QUERY, description="StatusCode(8位數字)", type=openapi.TYPE_STRING),
        ],
        )  
    @action(detail=False, methods=['get'])
    def check_receipt_by_statusCode(self, request):
        receipt_param = Receipt(
            StatusCode = request.GET.get('StatusCode')
        )
        result=self.service.check_receipt_by_statusCode(receipt_param)
        return JsonResponse(result)
       
    @swagger_auto_schema(operation_summary='發票兌獎(最近一期)By LedgerID',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="LedgerID", type=openapi.TYPE_STRING),
        ],
        )  
    @action(detail=False, methods=['get'])
    def check_receipt_by_LedgerID(self, request):
        ledger_param = Ledger(
            LedgerID = request.GET.get('LedgerID')
        )
        result=self.service.check_receipt_by_LedgerID(ledger_param)
        return JsonResponse(result)

    @swagger_auto_schema(operation_summary='發票兌獎(最近一期)By RecordID',
        manual_parameters=[
            openapi.Parameter('RecordID', openapi.IN_QUERY, description="RecordID", type=openapi.TYPE_STRING),
        ],
        )   
    @action(detail=False, methods=['get'])
    def check_receipt_by_RecordID(self, request):
        record_param = Record(
            RecordID = request.GET.get('RecordID'),
        )
        result=self.service.check_receipt_by_RecordID(record_param)
        return JsonResponse(result)
   
    

class SharePayViewSet(viewsets.GenericViewSet):
    service = SharePayService.SharePayService()
    queryset = SharePay.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = SharePaySerializer

    @swagger_auto_schema(operation_summary='計算帳本分帳總金額',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_sharepay_by_ledger(self, request):
        ledger_param = Ledger(
            LedgerID = request.GET.get('LedgerID')
        )
        result = self.service.get_sharepay_by_ledger(ledger_param)
        return JsonResponse(result)
       
    @swagger_auto_schema(operation_summary='取得紀錄分帳By RecordID',
        manual_parameters=[
            openapi.Parameter('RecordID', openapi.IN_QUERY, description="Record ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_sharepay_by_record(self, request):
        record_param = Record(
            RecordID = request.GET.get('RecordID'),
        )
        result = self.service.get_sharepay_by_record(record_param)
        return JsonResponse(result)

       
    @swagger_auto_schema(operation_summary='取得分帳者 By RecordID',
        manual_parameters=[
            openapi.Parameter('RecordID', openapi.IN_QUERY, description="Record ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_sharepay_user_by_record(self, request):
        record_param = Record(
            RecordID = request.GET.get('RecordID'),
        )
        result = self.service.get_sharepay_user_by_record(record_param)
        return JsonResponse(result)
   
   
   