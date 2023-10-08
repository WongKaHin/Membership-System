from email.policy import default
from operator import mod
from pyexpat import model
from re import T
from statistics import mode
from this import d
from django.db import models
import time
import uuid

# Create your models here.

class Member(models.Model):
    memid = models.CharField(max_length=43,primary_key=True)
    name = models.CharField(max_length=100)
    point = models.IntegerField(default=10000)
    pic = models.CharField(max_length=1000)
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.username
    

class History(models.Model):
    ordid = models.AutoField(primary_key=True)
    memid = models.CharField(max_length=43)
    cdate = models.DateTimeField() 
    gpoint = models.IntegerField(default=0)
    c_amount = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    appname = models.CharField(max_length=100)


class Behavior(models.Model):
    behid = models.IntegerField(default=0, primary_key=True)
    beh = models.CharField(max_length=100)
    cost = models.IntegerField(default=0)
    pic = models.FileField(max_length=100)
    time = models.IntegerField(default=0)

class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    memid = models.CharField(max_length=43)
    edate = models.DateField(auto_now=True)
    npoint = models.IntegerField(default=0)
    elist = models.CharField(max_length=100)

class Question(models.Model):
    memid = models.CharField(max_length=43)
    rdate = models.DateField(auto_now=True)
    disc = models.CharField(max_length=1000)

def UUIDrand():
    return str(uuid.uuid4())

class LOGIN(models.Model):
    FKcheck = models.CharField(max_length=36, default = UUIDrand)
    Rstate = models.CharField(max_length=42)
    RuserID = models.CharField(max_length=43)
    Raccess_code = models.CharField(max_length=43)

class App(models.Model):
    Appid = models.IntegerField(primary_key=True)
    Appname = models.CharField(max_length=20)
    url = models.CharField(max_length=100,default="None")
