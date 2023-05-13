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

from apiServices import UserService, LedgerService, LedgerAccessService


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
    serializer_class = RecordSerializer
    @swagger_auto_schema(operation_summary='新增紀錄',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'LedgerID': openapi.Schema(type=openapi.TYPE_STRING, description='要新增紀錄之帳本ID'),
                'ItemName': openapi.Schema(type=openapi.TYPE_STRING, description='物品名稱'),
                'ItemType': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型（收入/支出）'),
                'Cost': openapi.Schema(type=openapi.TYPE_STRING, description='費用(皆輸入正數)'),
                'Payby': openapi.Schema(type=openapi.TYPE_STRING, description='付錢者UserID(若空,則為create record者)'),
                'BoughtDate': openapi.Schema(type=openapi.TYPE_STRING, description='購買日期'),
            },),)    
    @action(detail=False, methods=['post'])
    def create_record(self, request):
        LedgerID = request.data['LedgerID']
        ItemName = request.data['ItemName']
        ItemType = request.data['ItemType']
        Cost = request.data['Cost']
        Payby = request.data['Payby']
        if(Payby ==''):
            Payby=request.user.UserID
        if(ItemType=="支出"):
            Cost=int(Cost)*(-1)
        BoughtDate = request.data['BoughtDate']
        if(BoughtDate == ''):
            BoughtDate = datetime.now()
        ledger = Ledger.objects.get(LedgerID=LedgerID)
        payby = User.objects.get(UserID=Payby)
        record = Record.objects.create(LedgerID=ledger, ItemName=ItemName, ItemType=ItemType, Cost=Cost, Payby=payby, BoughtDate=BoughtDate)
        record.save()
        return JsonResponse({'status': 'success', 'record': RecordSerializer(record).data})
    
    #delete record
    @swagger_auto_schema(operation_summary='刪除紀錄',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='要刪除的RecordID'),
            },),)    
    @action(detail=False, methods=['post'])
    def delete_record(self, request):
        RecordID = request.data['RecordID']
        record = Record.objects.get(RecordID=RecordID)
        record.delete()
        return JsonResponse({'status': 'success', 'record': RecordSerializer(record).data})
    
    #update_record
    @swagger_auto_schema(operation_summary='修改紀錄資料',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='要修改的紀錄ID'),
                'ItemName': openapi.Schema(type=openapi.TYPE_STRING, description='物品名稱'),
                'ItemType': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型（收入/支出）'),
                'Cost': openapi.Schema(type=openapi.TYPE_STRING, description='費用(皆輸入正數)'),
                'Payby': openapi.Schema(type=openapi.TYPE_STRING, description='物品類型'),
                'BoughtDate': openapi.Schema(type=openapi.TYPE_STRING, description='購買物品時間'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_record(self, request):
        RecordID = request.data['RecordID']
        record = Record.objects.get(RecordID=RecordID)
        if 'ItemName' in request.data:
            record.ItemName = request.data['ItemName']

        if 'ItemType' in request.data and 'Cost' in request.data:
            record.ItemType = request.data['ItemType']
            cost = request.data['Cost']
            if('ItemType'=="支出"):
                cost=int(cost)*(-1)
            record.Cost=cost
        elif 'ItemType' in request.data:
            record.ItemType = request.data['ItemType']
            cost=int(record.Cost)
            print(cost)
            if(record.ItemType=="支出" and cost>0):
                print("支出")
                cost=cost*(-1)
            elif(record.ItemType=="收入" and cost<0):
                print("收入")
                cost=cost*(-1)
            print(cost)
            record.Cost=cost
        elif 'Cost' in request.data:
            cost = int(request.data['Cost'])
            if(record.ItemType=="支出"):
                cost=cost*(-1)
            record.Cost=cost

        if 'Payby' in request.data:
            payby=request.data['Payby']
            record.Payby = User.objects.get(UserID=payby)
        if 'BoughtDate' in request.data:
            record.BoughtDate = request.data['BoughtDate']
        record.save()
        return JsonResponse({'status': 'success', 'record': RecordSerializer(record).data})
    
    # get records by ledger with ledgerID as parameter
    @swagger_auto_schema(operation_summary='取得單一帳本所有紀錄',
        manual_parameters=[
            openapi.Parameter('LedgerID', openapi.IN_QUERY, description="Ledger ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_records_by_ledger(self, request):
        LedgerID = request.GET.get('LedgerID')
        records = Record.objects.filter(LedgerID=LedgerID)
        return JsonResponse({'status': 'success', 'records': RecordSerializer(records, many=True).data})
    
    @swagger_auto_schema(operation_summary='取得當月收入',
       request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_earning_this_month(self, request):
        user = request.user
        Year = datetime.now().year
        Month = datetime.now().month
        start = str(Year)+'-'+str(Month)+"-1 00:00:00.000000"
        end = str(Year)+'-'+str(Month)+"-30 23:59:59.999999"
        Records=Record.objects.filter(Q(Payby=user.UserID) & Q(ItemType="收入") & Q(BoughtDate__range=(start,end)))
        earning=0
        for record in Records:
            earning+=record.Cost
        return JsonResponse({'status': 'success', 'this_month_earning': earning})
    
    @swagger_auto_schema(operation_summary='取得當月支出',
       request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_pay_this_month(self, request):
        user = request.user
        Year = datetime.now().year
        Month = datetime.now().month
        start = str(Year)+'-'+str(Month)+"-1 00:00:00.000000"
        end = str(Year)+'-'+str(Month)+"-30 23:59:59.999999"
        Records=Record.objects.filter(Q(Payby=user.UserID) & Q(ItemType="支出") & Q(BoughtDate__range=(start,end)))
        pay=0
        for record in Records:
            pay+=record.Cost
        return JsonResponse({'status': 'success', 'this_monyh_pay': pay})

class ReceiptViewSet(viewsets.GenericViewSet):
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
        RecordID = request.data['RecordID']
        if(Receipt.objects.filter(RecordID=RecordID).exists()):
            return JsonResponse({'status': 'fail', 'error': 'This recordID\'s receipt already exist'})
        try:
            record = Record.objects.get(RecordID=RecordID)
        except Record.DoesNotExist:
            record = None
        if(record is None):
            return JsonResponse({'status': 'fail', 'error': 'record does not exist'})
        StatusCode = request.data['StatusCode']
        if(len(StatusCode) != 8 or StatusCode.isnumeric()==False):
            return JsonResponse({'status': 'fail', 'error': 'Statuscode does not legal! Need 8 numbers.'})
        BuyDate = record.BoughtDate
        receipt = Receipt.objects.create(RecordID=record, BuyDate=BuyDate, StatusCode=StatusCode)
        receipt.save()
        return JsonResponse({'status': 'success', 'receipt': ReceiptSerializer(receipt).data})

    @swagger_auto_schema(operation_summary='刪除發票',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'ReceiptID': openapi.Schema(type=openapi.TYPE_STRING, description='要刪除的ReceiptID'),
            },),)    
    @action(detail=False, methods=['post'])
    def delete_receipt(self, request):
        ReceiptID = request.data['ReceiptID']
        try:
            receipt = Receipt.objects.get(ReceiptID=ReceiptID)
        except Receipt.DoesNotExist:
            receipt = None
        if(receipt is None):
            return JsonResponse({'status': 'fail', 'error': 'receipt does not exist'})
        receipt.delete()
        return JsonResponse({'status': 'success', 'record': ReceiptSerializer(receipt).data})
    
    @swagger_auto_schema(operation_summary='修改發票號碼',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'ReceiptID': openapi.Schema(type=openapi.TYPE_STRING, description='要修改的發票ID'),
                'StatusCode': openapi.Schema(type=openapi.TYPE_STRING, description='發票號碼(8位數字)'),
            },),)    
    @action(detail=False, methods=['post'])
    def update_receipt_statusCode(self, request):
        ReceiptID = request.data['ReceiptID']
        receipt = Receipt.objects.get(ReceiptID=ReceiptID)
        # check if user have Owner access level to the ledger
        #if(record.recordaccess_set.filter(UserID=request.user.UserID, AccessLevel="Owner").exists() == False):
        #    return JsonResponse({'status': 'fail', 'error': 'user have no access to the ledger'})
        StatusCode=request.data['StatusCode']
        if(len(StatusCode) != 8 or StatusCode.isnumeric()==False):
            return JsonResponse({'status': 'fail', 'error': 'Statuscode does not legal! Need 8 numbers.'})
        if 'StatusCode' in request.data:
            receipt.StatusCode = StatusCode
        receipt.save()
        return JsonResponse({'status': 'success', 'receipt': ReceiptSerializer(receipt).data})
    
    @swagger_auto_schema(operation_summary='取得使用者自己（有觀看權限）的所有發票',
         request_body=None
        )    
    @action(detail=False, methods=['get'])
    def get_receipts(self, request):
        user = request.user
        ledger_list = Ledger.objects.filter(OwnerID = user.UserID)
        if(ledger_list.count() == 0):
            return JsonResponse({'status': 'fail', 'error': 'User has no ledger'})
        #取得使用者自己所有ledger之record
        ledger_filter = Q()
        for ledger in ledger_list:
             ledger_filter = ledger_filter | Q(LedgerID=ledger.LedgerID)
        record_list=Record.objects.filter(ledger_filter)
        if(record_list.count() == 0):
            return JsonResponse({'status': 'fail', 'error': 'User has no record'})
        #取得使用者自己所有record之receipt
        record_filter = Q()
        for record in record_list:
             record_filter = record_filter | Q(RecordID=record.RecordID)
        receipts=Receipt.objects.filter(record_filter)
        if(receipts.count() == 0):
            return JsonResponse({'status': 'fail', 'error': 'User has no receipt'})
        return JsonResponse({'status': 'success', 'receipts': ReceiptSerializer(receipts, many=True).data})
    
    @swagger_auto_schema(operation_summary='取得紀錄之發票',
        manual_parameters=[
            openapi.Parameter('RecordID', openapi.IN_QUERY, description="Record ID", type=openapi.TYPE_STRING),
        ],
        )    
    @action(detail=False, methods=['get'])
    def get_receipt_by_recordID(self, request):
        RecordID = request.GET.get('RecordID')
        receipt = Receipt.objects.filter(RecordID=RecordID)
        return JsonResponse({'status': 'success', 'receipts': ReceiptSerializer(receipt, many=True).data})

class SharePayViewSet(viewsets.GenericViewSet):
    queryset = SharePay.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = SharePaySerializer
    @swagger_auto_schema(operation_summary='新增分帳',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
            properties={
                'RecordID': openapi.Schema(type=openapi.TYPE_STRING, description='分帳紀錄ID'),
                'ShouldPay': openapi.Schema(type=openapi.TYPE_STRING, description='已分帳後金額'),
                'ShareUserID': openapi.Schema(type=openapi.TYPE_STRING, description='分帳者ID'),
            },),)    
    @action(detail=False, methods=['post'])
    def add_sharepay(self, request):
        RecordID = request.data['RecordID']
        record = Record.objects.get(RecordID = RecordID)
        ShouldPay = request.data['ShouldPay']
        ShareUserID = request.data['ShareUserID']
        share_user=User.objects.get(UserID = ShareUserID)
        sharepay = SharePay.objects.create(RecordID=record, ShouldPay=ShouldPay, ShareUser = share_user)
        sharepay.save()
        return JsonResponse({'status': 'success', 'sharepay': SharePaySerializer(sharepay).data})
   