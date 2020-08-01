from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Expense(models.Model):
    text = models.CharField(max_length=253)
    date = models.DateTimeField()
    amount = models.BigIntegerField()
    user =  models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.text}\t{self.amount}\t{self.date}"

class Income(models.Model):
    text = models.CharField(max_length=253)
    date = models.DateTimeField()
    amount = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.text}\t{self.amount}\t{self.date}"

class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=48)
    def __str__(self):
        return f"{self.user} token"