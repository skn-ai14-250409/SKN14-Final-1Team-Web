from django.contrib import admin
from django.conf import settings
from django.apps import apps
from django.db import transaction
from .models import Status, ApprovalLog, User

# Register your models here.
admin.site.register(User)
admin.site.register(ApprovalLog)
