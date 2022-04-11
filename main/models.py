from django.db import models


# Create your models here.
class UserModel(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    regNo = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    div = models.CharField(max_length=20)
    profile = models.CharField(max_length=200)
