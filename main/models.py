from django.db import models


# Create your models here.
class UserModel(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    caste = models.CharField(max_length=30)
    sub_caste = models.CharField(max_length=30)
    nationality = models.CharField(max_length=100)
    regNo = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    div = models.CharField(max_length=20)
    profile = models.CharField(max_length=200)
    year = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

