from .models import *
from rest_framework import viewsets,permissions
from .serializer import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password    
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from drf_yasg import openapi


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser,)
    
    @swagger_auto_schema(operation_summary='登入',)
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
    @action(detail=False, methods=['post'])
    def logout(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        logout(request)
        return JsonResponse({'status': 'success'})
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
    
    @action(detail=False, methods=['get'])
    def get_ledgers(self, request):
        # return the ledgers that the user has access by checking the ledger_access table
        ledgers = Ledger.objects.filter(ledgeraccess__UserID=request.user)
        return JsonResponse({'status': 'success', 'ledgers': LedgerSerializer(ledgers, many=True).data})
    


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
    @action(detail=False, methods=['get'])
    def get_records_by_ledger(self, request):
        LedgerID = request.GET.get('LedgerID')
        records = Record.objects.filter(LedgerID=LedgerID)
        return JsonResponse({'status': 'success', 'records': RecordSerializer(records, many=True).data})