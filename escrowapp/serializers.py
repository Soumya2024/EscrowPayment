from rest_framework import serializers
from .models import EscrowTransaction, EscrowCustomer, RegisterModel
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import RegisterModel
import re

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import RegisterModel


# Transection Serializer
# class EscrowTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EscrowTransaction
#         fields = ['id', 'payer', 'payee_phone', 'amount', 'status', 'escrow_account_id']
#         read_only_fields = ['payer', 'status', 'escrow_account_id']


# Register Serialization
# class RegistrationSerializer(serializers.ModelSerializer):
#     password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
#     class Meta:
#         model = RegisterModel
#         fields = ['username', 'email', 'password', 'password2', 'phone_number', 'address']
#         read_only = ['id']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }
    
#     def validate_phone_number(self, value):
#         pattern = re.compile(r'^\+?1?\d{9,15}$')
#         if not pattern.match(value):
#             raise serializers.ValidationError("Invalid phone number format")
#         return value
    
#     def validate_email(self, value):
#         if RegisterModel.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email already registered")
#         return value
    
#     def validate(self, data):
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError({"password": "Passwords must match"})
#         return data
    
#     def create(self, validated_data):
#         validated_data.pop('password2')
        
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
        
#         register_user = RegisterModel.objects.create(
#             username=user,
#             email=validated_data['email'],
#             phone_number=validated_data['phone_number'],
#             address=validated_data.get('address', ''),
#             password=user.password
#         )
        
#         self.send_registration_email(register_user)
        
#         return register_user
    
#     def send_registration_email(self, user):
#         subject = 'Welcome to Our Platform!'
#         message = f"""
#         Hello {user.username},
        
#         Thank you for registering with our platform! Your account has been created successfully.
        
#         Please verify your email address to activate your account.
        
#         Best regards,
#         Your Platform Team
#         """
        
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             fail_silently=False,
#         )

# class RegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RegisterModel
#         fields = ['username', 'password', 'password2', 'email', 'phone_number', 'address']
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'password2': {'write_only': True}
#         }
        
#     def username_field(self, value):
#         if RegisterModel.objects.filter(User = value).exists():
#             raise serializers.ValidationError('Username already exists')
#         return value
#         # return self.fields['username'].get_attribute(self.instance)

#     def validate_phone_number(self, value):
#         pattern = re.compile(r'^\+?1?\d{9,15}$')
#         if not pattern.match(value):
#             raise serializers.ValidationError("Invalid phone number format")
#         return value
    
#     def validate_email(self, value):
#         if RegisterModel.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email already registered")
#         return value
    
#     def create(self, validated_data):
#         if validated_data['password'] != validated_data['password2']:
#             raise serializers.ValidationError({"password": "Passwords do not match."})
        
#         validated_data.pop('password2')

#         register_model = RegisterModel.objects.create(**validated_data)

#         register_model.password = validated_data['password']
#         register_model.save()

#         return register_model


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RegisterModel


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterModel
        fields = ['username', 'password', 'password2', 'email', 'phone_number', 'address']

    def username_field(self, value):
        if RegisterModel.objects.filter(User = value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
        # return self.fields['username'].get_attribute(self.instance)

    def validate_phone_number(self, value):
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def validate_email(self, value):
        if RegisterModel.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        if validated_data['password'] != validated_data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})

        # Create the User instance
        user = User.objects.create_user(
            username=validated_data['username'], 
            password=validated_data['password'],
            email=validated_data['email'],
        )

        # Create the RegisterModel instance
        register_model = RegisterModel.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            address=validated_data.get('address', ''), 
        )

        return register_model

# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        
        user = authenticate(username=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials or inactive user.")
        
        return {"user_id": user.id, "email": user.email, "is_active": user.is_active}


# TimeZone Serializer For Timezone(Created_at & Updated_at) 
# from utils.utils import get_user_timezone

# class TimezoneAwareSerializer(serializers.ModelSerializer):
#     local_created_at = serializers.SerializerMethodField()
#     local_updated_at = serializers.SerializerMethodField()

#     class Meta:
#         model = RegisterModel
#         fields = ['created_at', 'updated_at', 'local_created_at', 'local_updated_at']

#     def get_local_created_at(self, obj):
#         user_tz = get_user_timezone(self.context['request'])
#         return obj.created_at.astimezone(user_tz).isoformat()

#     def get_local_updated_at(self, obj):
#         user_tz = get_user_timezone(self.context['request'])
#         return obj.updated_at.astimezone(user_tz).isoformat()



class EscrowTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscrowTransaction
        fields = ['id', 'payer', 'payee_email', 'amount', 'description', 'status', 'escrow_account_id']
        read_only_fields = ['payer', 'status', 'escrow_account_id']

from rest_framework import serializers

# Create Customer Serializer 
# class EscrowCustomerSerializer(serializers.Serializer):
#     customer_id = serializers.IntegerField(read_only=True)
#     email = serializers.EmailField()
#     first_name = serializers.CharField(max_length=50)
#     middle_name = serializers.CharField(max_length=50, required=False)
#     last_name = serializers.CharField(max_length=50)
#     address_line1 = serializers.CharField(max_length=100)
#     address_line2 = serializers.CharField(max_length=100, required=False)
#     city = serializers.CharField(max_length=50)
#     state = serializers.CharField(max_length=50)
#     country = serializers.CharField(max_length=2)
#     post_code = serializers.CharField(max_length=20)
#     phone_number = serializers.CharField(max_length=20)

# Register User
# class RegisterUserSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password']
#         )
#         return user
    
#     class Meta:
#         model = User
#         fields = ['customer_id', 'other_fields']

#     def validate_customer_id(self, value):
#         try:
#             customer = User.objects.get(id=value)
#             if not customer.is_active:
#                 raise serializers.ValidationError("Customer is not active")
#         except customer.DoesNotExist:
#             raise serializers.ValidationError("Customer does not exist")
#         return value

# Update Customer User
class UpdateEscrowCustomerSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=50, required=False)
    middle_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    address_line1 = serializers.CharField(max_length=100, required=False)
    address_line2 = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=50, required=False)
    state = serializers.CharField(max_length=50, required=False)
    country = serializers.CharField(max_length=2, required=False)
    post_code = serializers.CharField(max_length=20, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)


from rest_framework import serializers
from .models import EscrowCustomer, DisbursementMethod, BankAddress
from django.utils.dateparse import parse_date, parse_datetime
from datetime import datetime


from rest_framework import serializers

class BankAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAddress
        fields = ['city', 'state', 'country']

class DisbursementMethodSerializer(serializers.ModelSerializer):
    bank_address = BankAddressSerializer()

    class Meta:
        model = DisbursementMethod
        fields = [
            'account_name', 'account_type', 'bank_aba_routing_number', 
            'bank_account_number', 'bank_address', 'bank_name', 'currency', 'type'
        ]

class EscrowCustomerSerializer(serializers.ModelSerializer):
    disbursement_methods = DisbursementMethodSerializer(many=True)

    class Meta:
        model = EscrowCustomer
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 
            'address_line1', 'address_line2', 'city', 'state', 'country', 
            'post_code', 'escrow_customer_id', 'date_of_birth', 
            'disbursement_methods', 'webhook_url'
        ]

    def create(self, validated_data):
        disbursement_methods_data = validated_data.pop('disbursement_methods')
        
        # Handle date_of_birth validation
        date_of_birth = validated_data.get('date_of_birth')
        if isinstance(date_of_birth, str):
            validated_data['date_of_birth'] = parse_datetime(date_of_birth)

        escrow_customer = EscrowCustomer.objects.create(**validated_data)

        for disbursement_data in disbursement_methods_data:
            bank_address_data = disbursement_data.pop('bank_address')
            bank_address = BankAddress.objects.create(**bank_address_data)
            DisbursementMethod.objects.create(
                escrow_customer=escrow_customer,
                bank_address=bank_address,
                **disbursement_data
            )

        return escrow_customer
    
# from rest_framework import generics
# from .models import EscrowCustomer
# from .serializers import EscrowCustomerSerializer

# class EscrowCustomerCreateView(generics.CreateAPIView):
#     queryset = EscrowCustomer.objects.all()
#     serializer_class = EscrowCustomerSerializer



# class EscrowCustomerSerializer(serializers.ModelSerializer):
#     disbursement_methods = DisbursementMethodSerializer(many=True)

#     class Meta:
#         model = EscrowCustomer
#         fields = [
#             'first_name', 'middle_name', 'last_name', 'email', 'phone_number',
#             'address_line1', 'address_line2', 'city', 'state', 'country', 'post_code',
#             'escrow_customer_id', 'date_of_birth', 'disbursement_methods', 'webhook_url'
#         ]

#     def validate_date_of_birth(self, value):
#         print(f"Validating date_of_birth: {value}")
#         """Validate the date_of_birth to ensure it's in the correct format"""
#         if isinstance(value, str):
#             parsed_date = parse_datetime(value)
#             print(f"This is parsed_date data{parsed_date}")
#             if parsed_date is None:
#                 raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
#             return parsed_date
#         elif isinstance(value, datetime):
#             return value
#         else:
#             raise serializers.ValidationError("The date of birth must be a valid date object or a string in YYYY-MM-DD format.")

#     def create(self, validated_data):
#         disbursement_methods_data = validated_data.pop('disbursement_methods')
        
#         escrow_customer = EscrowCustomer.objects.create(**validated_data)

#         for disbursement_data in disbursement_methods_data:
#             bank_address_data = disbursement_data.pop('bank_address')
#             bank_address = BankAddress.objects.create(**bank_address_data)
#             DisbursementMethod.objects.create(
#                 escrow_customer=escrow_customer,
#                 bank_address=bank_address,
#                 **disbursement_data
#             )

#         return escrow_customer




from rest_framework import serializers
from .models import Transaction, Schedule, Item, Party

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['amount', 'payer_customer', 'beneficiary_customer']

class ItemSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(many=True)
    extra_attributes = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['title', 'description', 'type', 'inspection_period', 'quantity', 
                 'schedule', 'extra_attributes']

    def get_extra_attributes(self, obj):
        return {
            'image_url': obj.image_url,
            'merchant_url': obj.merchant_url
        }

    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule')
        item = Item.objects.create(**validated_data)
        for schedule in schedule_data:
            Schedule.objects.create(item=item, **schedule)
        return item

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['role', 'customer']

class TransactionSerializer(serializers.ModelSerializer):
    parties = PartySerializer(many=True)
    items = ItemSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['parties', 'currency', 'description', 'items']

    def create(self, validated_data):
        parties_data = validated_data.pop('parties')
        items_data = validated_data.pop('items')
        
        transaction = Transaction.objects.create(**validated_data)
        
        for party_data in parties_data:
            Party.objects.create(transaction=transaction, **party_data)
            
        for item_data in items_data:
            schedule_data = item_data.pop('schedule')
            item = Item.objects.create(transaction=transaction, **item_data)
            
            for schedule in schedule_data:
                Schedule.objects.create(item=item, **schedule)
        
        return transaction