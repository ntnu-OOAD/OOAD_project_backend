from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Ledger)
admin.site.register(LedgerAccess)
admin.site.register(Record)
admin.site.register(SharePay)
admin.site.register(Receipt)