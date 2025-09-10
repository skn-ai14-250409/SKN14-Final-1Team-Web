from django.contrib import admin
from .models import ApprovalLog, User

# Register your models here.
admin.site.register(User)
admin.site.register(ApprovalLog)
