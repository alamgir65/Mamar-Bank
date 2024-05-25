from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE,GENDER_TYPE
# Create your models here.

class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    gender = models.CharField(max_length=20, choices=GENDER_TYPE)
    initial_deposit_date = models.DateField(auto_now_add=True)
    birth_date = models.DateField(null=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_no = models.IntegerField(unique=True)
    is_Bankrupt = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user.username} - {self.account_no}'

class UserAdress(models.Model):
    user = models.OneToOneField(User, related_name='address', on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    
    def __str__(self):
        return f'{self.user.username}'
    
