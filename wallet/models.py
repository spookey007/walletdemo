from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=42, unique=True, blank=True, null=True)
    private_key = models.CharField(max_length=64, blank=True, null=True)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_address = models.CharField(max_length=42)
    tx_hash = models.CharField(max_length=66)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
