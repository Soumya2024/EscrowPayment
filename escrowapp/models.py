import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
import pytz



# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.


# class RegisterModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     username = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
#     # User, on_delete=models.CASCADE, related_name='register'
#     password = models.CharField(max_length=30, unique=False, verbose_name='Password')
#     password2 = models.CharField(max_length=30, unique=False)
#     email = models.EmailField(max_length=100, unique=True)
#     phone_number = models.CharField(max_length=20, unique=True)
#     address = models.CharField(max_length=200, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True) 
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)
#     is_verified = models.BooleanField(default=False)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'phone_number']

#     @property
#     def name(self):
#         if self.user_id is not None:
#             return self.user.username
        
#     def __str__(self):
#         return f"RegisterModel {self.id}: {self.username} to {self.phone_number} - {self.email} - {self.address}"

    
#     # @property
#     # def name(self):
#     #     return self.username.username 
    
#     # def save(self, *args, **kwargs):
#     #     if not self.pk:
#     #         self.created_at = timezone.now()
#     #     self.updated_at = timezone.now()
#     #     super().save(*args, **kwargs)

#     # def tokens(self):
#     #     refresh = RefreshToken.for_user(self)
#     #     return {
#     #         'refresh': str(refresh),
#     #         'access': str(refresh.access_token), 
#     #     }


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email to log in
    REQUIRED_FIELDS = ["username"]  # Additional required fields when creating a superuser

    def __str__(self):
        return self.email



# from django.contrib.auth import get_user_model
# User = get_user_model()



# Transection Model
# class EscrowTransaction(models.Model):
#     payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_transactions')
#     payee_phone = models.CharField(max_length=15)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=[('in_escrow', 'In Escrow'), ('released', 'Released'), ('refunded', 'Refunded')])
#     escrow_account_id = models.CharField(max_length=100)

#     def __str__(self):
#         return f"Transaction {self.id}: {self.payer.username} to {self.payee_phone} - {self.amount} - {self.status}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EscrowTransaction(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_transactions')
    # payer = models.ForeignKey(User, on_delete=models.CASCADE)
    payee_phone = models.CharField(max_length=15)
    payee_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('in_escrow', 'In Escrow'), ('released', 'Released'), ('refunded', 'Refunded')])
    escrow_account_id = models.CharField(max_length=50)

    def __str__(self):
        # return f"Transaction {self.id} - {self.status}"
        return f"Transaction {self.id}: {self.payer.username} to {self.payee_phone} - {self.amount} - {self.status}"



# class EscrowCustomer(models.Model):
#     customer_id = models.AutoField(unique=True,primary_key=True)
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=50)
#     middle_name = models.CharField(max_length=50, blank=True, null=True)
#     last_name = models.CharField(max_length=50)
#     address_line1 = models.CharField(max_length=100)
#     address_line2 = models.CharField(max_length=100, blank=True, null=True)
#     city = models.CharField(max_length=50)
#     state = models.CharField(max_length=50)
#     country = models.CharField(max_length=2) 
#     post_code = models.CharField(max_length=20)
#     phone_number = models.CharField(max_length=20)
#     escrow_customer_id = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.email}"

# Escrow Account 

# from django.db import models

# class BankAddress(models.Model):
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     country = models.CharField(max_length=50)


# class DisbursementMethod(models.Model):
#     escrow_customer = models.ForeignKey('EscrowCustomer', on_delete=models.CASCADE, related_name='disbursement_methods')
#     account_name = models.CharField(max_length=100)
#     account_type = models.CharField(max_length=20, choices=(("savings", "Savings"), ("checking", "Checking")))
#     bank_aba_routing_number = models.CharField(max_length=20)
#     bank_account_number = models.CharField(max_length=20)
#     bank_address = models.OneToOneField(BankAddress, on_delete=models.CASCADE)
#     bank_name = models.CharField(max_length=100)
#     currency = models.CharField(max_length=3)
#     type = models.CharField(max_length=20, default="ach") 

# class EscrowCustomer(models.Model):
#     customer_id = models.AutoField(unique=True,primary_key=True)
#     first_name = models.CharField(max_length=50)
#     middle_name = models.CharField(max_length=50, blank=True, null=True)
#     last_name = models.CharField(max_length=50)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=20)
#     address_line1 = models.CharField(max_length=100)
#     address_line2 = models.CharField(max_length=100)
#     city = models.CharField(max_length=50)
#     state = models.CharField(max_length=50)
#     country = models.CharField(max_length=2)
#     post_code = models.CharField(max_length=20)
#     escrow_customer_id = models.CharField(max_length=100, blank=True, null=True)
#     # date_of_birth = models.DateField(default="1900-01-01")
#     date_of_birth = models.DateTimeField(null=True, blank=True)
#     disbursement_methods = models.ManyToManyField(DisbursementMethod)
#     webhook_url = models.URLField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} - {self.email}"


from django.db import models

class BankAddress(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)  

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

class DisbursementMethod(models.Model):
    CURRENCY_CHOICES = (
        ("usd", "US Dollar"),
        ("eur", "Euro"),
        ("gbp", "British Pound"),
        ("jpy", "Japanese Yen"),
        ("chf", "Swiss Franc"),
        ("aud", "Australian Dollar"),
        ("cad", "Canadian Dollar"),
        ("cny", "Chinese Renminbi"),
        ("hkd", "Hong Kong Dollar"),
        ("inr", "Indian Rupee"),
        ("krw", "South Korean Won"),
        ("mxn", "Mexican Peso"),
        ("nzd", "New Zealand Dollar"),
        ("rub", "Russian Ruble"),
        ("sgd", "Singapore Dollar"),
        ("zar   ", "South African Rand"))   

    escrow_customer = models.ForeignKey("EscrowCustomer", on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=(("savings", "Savings"), ("checking", "Checking")))
    bank_aba_routing_number = models.CharField(max_length=20)
    bank_account_number = models.CharField(max_length=20)
    bank_address = models.ForeignKey(BankAddress, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    currency = models.CharField(max_length=6, choices=CURRENCY_CHOICES)
    type = models.CharField(max_length=20, default="ach")

    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"

class EscrowCustomer(models.Model):
    customer_id = models.AutoField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True) 
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=100) 
    post_code = models.CharField(max_length=20)
    escrow_customer_id = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    disbursement_methods = models.ManyToManyField(DisbursementMethod, related_name='customers')
    webhook_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"






# Payment For Marchendise Payment
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Transaction(models.Model):
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('aud', 'AUD'),
        ('euro', 'EURO'),
        ('gbp', 'GBP'),
        ('cad', 'CAD'),
    ]

    description = models.CharField(max_length=255)
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, default='usd')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.description}"

class Party(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('broker', 'Broker'),
        ('partner', 'Partner'),
    ]

    transaction = models.ForeignKey(Transaction, related_name='parties', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    customer = models.EmailField()
    privacy = models.BooleanField(default=False)

    class Meta:
        unique_together = ['transaction', 'role', 'customer']

class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ('domain_name', 'Domain Name'),
        ('domain_name_holding', 'Domain Name Holding'),
        ('general_merchandise', 'General Merchandise'),
        ('milestone', 'Milestone'),
        ('motor_vehicle', 'Motor Vehicle'),
        ('broker_fee', 'Broker Fee'),
        ('partner_fee', 'Partner Fee'),
        ('shipping_fee', 'Shipping Fee'),
    ]

    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    inspection_period = models.IntegerField(default=259200)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    image_url = models.URLField(blank=True, null=True)
    merchant_url = models.URLField(blank=True, null=True)

class Schedule(models.Model):
    item = models.ForeignKey(Item, related_name='schedule', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payer_customer = models.EmailField()
    beneficiary_customer = models.EmailField()