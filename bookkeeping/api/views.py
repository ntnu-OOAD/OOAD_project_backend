from .models import *
from rest_framework import viewsets,permissions
from .serializer import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password    
from django.http import JsonResponse

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer
    @action(detail=False, methods=['post'])
    def login(self, request):
        UserID = request.data['UserID']
        password = request.data['password']
        user = authenticate(UserID=UserID, password=password)
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
        UserID = request.data['UserID']
        nickname = request.data['nickname']
        password = request.data['password']
        # check if UserID is already taken
        if User.objects.filter(UserID=UserID).exists():
            return JsonResponse({'status': 'fail', 'error': 'UserID already taken'})
        user = User.objects.create_user(UserID=UserID, nickname=nickname, password=password)
        user.save()
        return JsonResponse({'status': 'success'})
    @action(detail=False, methods=['get'])
    def get_user(self, request):
        # check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'fail', 'error': 'user not logged in'})
        user = User.objects.get(UserID=request.user.UserID)
        return JsonResponse({'status': 'success', 'user': UserSerializer(user).data})
    
class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = LedgerSerializer
    @action(detail=False, methods=['post'])
    def create_ledger(self, request):
        LedgerType = request.data['LedgerType']
        OwnerID = request.user.UserID
        user = User.objects.get(UserID=OwnerID)
        ledger = Ledger.objects.create(OwnerID=user, LedgerType=LedgerType)
        ledger.save()
        ledger_access = LedgerAccess.objects.create(LedgerID=ledger, UserID=user, AccessLevel="Owner")
        ledger_access.save()
        return JsonResponse({'status': 'success', 'ledger': LedgerSerializer(ledger).data})
    
    @action(detail=False, methods=['get'])
    def get_ledgers(self, request):
        # return the ledgers that the user has access by checking the ledger_access table
        ledgers = Ledger.objects.filter(ledgeraccess__UserID=request.user)
        return JsonResponse({'status': 'success', 'ledgers': LedgerSerializer(ledgers, many=True).data})
    

class LedgerAccessViewSet(viewsets.ModelViewSet):
    queryset = LedgerAccess.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = LedgerAccessSerializer
    @action(detail=False, methods=['post'])
    def create_ledger_access(self, request):
        LedgerID = request.data['LedgerID']
        UserID = request.data['UserID']
        AccessLevel = request.data['AccessLevel']
        ledger_access = LedgerAccess.objects.create(LedgerID=LedgerID, UserID=UserID, AccessLevel=AccessLevel)
        ledger_access.save()
        return JsonResponse({'status': 'success', 'ledger_access': LedgerAccessSerializer(ledger_access).data})

class RecordViewSet(viewsets.ModelViewSet):
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
        record = Record.objects.create(LedgerID=LedgerID, ItemName=ItemName, ItemType=ItemType, Cost=Cost, Payby=Payby, BoughtDate=BoughtDate)
        record.save()
        return JsonResponse({'status': 'success', 'record': RecordSerializer(record).data})

    @action(detail=False, methods=['get'])
    def get_records_by_ledger(self, request):
        LedgerID = request.GET.get('LedgerID')
        records = Record.objects.filter(LedgerID=LedgerID)
        return JsonResponse({'status': 'success', 'records': RecordSerializer(records, many=True).data})