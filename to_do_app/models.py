from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class User_details(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=100,default="")
    status = models.CharField(max_length=200,default="")
    
    def __str__(self):
        return self.user.username

class Task_add(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    task_id = models.AutoField(primary_key= True)
    title = models.CharField(max_length=10000,default="")
    content = models.CharField(max_length=100000,default="",null=True,blank=True)
    date = models.DateField()
    class_name = models.CharField(max_length=1000000,default="")
    status = models.CharField(max_length=100,default="active")

    def __str__(self):
        return str(self.user.id) + "-" + str(self.task_id) + "-" + str(self.date)

class task_date(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return str(self.user.id) + "-" + str(self.date)
    
class Verification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=100,default="")
    purpose = models.CharField(max_length=100,default="")
    def __str__(self):
        return self.user.username + "-" + self.purpose