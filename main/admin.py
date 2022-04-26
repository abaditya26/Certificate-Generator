from django.contrib import admin

# Register your models here.
from main.models import UserModel, CertificateRequestModel, AdminModel

admin.site.register(UserModel)
admin.site.register(CertificateRequestModel)
admin.site.register(AdminModel)
