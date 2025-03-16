import requests, logging
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from .payment_gateway import PaymentGateway
from .models import EscrowTransaction
from .models import EscrowCustomer, DisbursementMethod, BankAddress
from .models import EscrowCustomer
from .serializers import EscrowTransactionSerializer
from .serializers import EscrowCustomerSerializer
from .serializers import DisbursementMethodSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer

logger = logging.getLogger(__name__)

# Create your views here.

# Register Account View
# class RegisterUserView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterUserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, {(" User Registered Successfully")}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, {(" Input the correct Value ")}, status=status.HTTP_400_BAD_REQUEST)
#     # def post(self, request):
#     #     serializer = RegisterUserSerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class RegistrationView(APIView):
#     permission_classes = (AllowAny,)
#     serializer_class = RegistrationSerializer
    
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             user_uuid = uuid.uuid4()
#             response_data = {
#                 'status': True,
#                 'message': "f '{username}' Registration successful!",
#                 'data': {
#                     'uuid': str(user_uuid),
#                     'username': user.username.username,
#                     'email': user.email,
#                     'phone_number': user.phone_number,
#                     'tokens': user.tokens()
#                 }
#             }
            
#             return Response(response_data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import RegisterModel
from .serializers import RegistrationSerializer

class RegistrationView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    
    queryset = RegisterModel.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # if response.status_code == 201:
        return Response(
            {
                "message": "User registered successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        # else:
        #     return Response(response_data, status=response.status_code)
        



class LoginView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class CreateEscrowCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EscrowCustomerSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            disbursement_methods_payload = []
            for disbursement_method_data in data['disbursement_methods']:
                disbursement_methods_payload.append({
                    "account_name": disbursement_method_data['account_name'],
                    "account_type": disbursement_method_data['account_type'],
                    "bank_aba_routing_number": disbursement_method_data['bank_aba_routing_number'],
                    "bank_account_number": disbursement_method_data['bank_account_number'],
                    "bank_address": {
                        "city": disbursement_method_data['bank_address']['city'],
                        "state": disbursement_method_data['bank_address']['state'],
                        "country": disbursement_method_data['bank_address']['country']
                    },
                    "bank_name": disbursement_method_data['bank_name'],
                    "currency": disbursement_method_data['currency'],
                    "type": disbursement_method_data['type']
                    #get('type', 'ach')
                })

                # disbursement_methods_payload.append({
                #     "account_name": disbursement_method_data['account_name'],
                #     "account_type": disbursement_method_data['account_type'],
                #     "bank_aba_routing_number": disbursement_method_data['bank_aba_routing_number'],
                #     "bank_account_number": disbursement_method_data['bank_account_number'],
                #     "bank_address": {
                #         "city": disbursement_method_data['bank_address']['city'],
                #         "state": disbursement_method_data['bank_address']['state'],
                #         "country": disbursement_method_data['bank_address']['country']
                #     },
                #     "bank_name": disbursement_method_data['bank_name'],
                #     "currency": disbursement_method_data['currency'],
                #     "type": disbursement_method_data['type']
                # })

            payload = {
                "email": data['email'],
                "first_name": data['first_name'],
                "middle_name": data.get('middle_name', ""),
                "last_name": data['last_name'],
                "address": {
                    "line1": data['address_line1'],
                    "line2": data.get('address_line2', ""),
                    "city": data['city'],
                    "state": data['state'],
                    "country": data['country'],
                    "post_code": data['post_code']
                },
                "date_of_birth": data['date_of_birth'].strftime('%Y-%m-%d'),
                "phone_number": data['phone_number'],
                "disbursement_methods": disbursement_methods_payload,
                "webhooks": [{
                    "url": data.get('webhook_url', '')
                }]
            }

            escrow_url = 'https://api.escrow.com/2017-09-01/customer'
            email = settings.ESCROW_API_EMAIL
            api_key = settings.ESCROW_API_KEY

            try:
                response = requests.post(escrow_url, auth=(email, api_key), json=payload)
                response_data = response.json()

                if response.status_code == 201:
                    with transaction.atomic():
                        escrow_customer, created = EscrowCustomer.objects.update_or_create(
                            email=data['email'],
                            defaults={
                                'first_name': data['first_name'],
                                'middle_name': data.get('middle_name', ""),
                                'last_name': data['last_name'],
                                'address_line1': data['address_line1'],
                                'address_line2': data.get('address_line2', ""),
                                'city': data['city'],
                                'state': data['state'],
                                'country': data['country'],
                                'post_code': data['post_code'],
                                'phone_number': data['phone_number'],
                                'escrow_customer_id': response_data.get('id')
                            }
                        )

                        disbursement_methods_data = data['disbursement_methods']
                        for disbursement_method_data in disbursement_methods_data:
                            bank_address_data = disbursement_method_data['bank_address']
                            bank_address = BankAddress.objects.create(
                                city=bank_address_data['city'],
                                state=bank_address_data['state'],
                                country=bank_address_data['country'] 
                            )
                            DisbursementMethod.objects.create(
                                escrow_customer=escrow_customer,
                                account_name=disbursement_method_data['account_name'],
                                account_type=disbursement_method_data['account_type'],
                                bank_aba_routing_number=disbursement_method_data['bank_aba_routing_number'],
                                bank_account_number=disbursement_method_data['bank_account_number'],
                                bank_address=bank_address,
                                bank_name=disbursement_method_data['bank_name'],
                                currency=disbursement_method_data['currency'],
                                type=disbursement_method_data['type']
                            )

                    status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                    return Response(response_data, status=status_code)
                else:
                    return Response(response_data, status=response.status_code)

            except requests.RequestException as e:
                return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from .models import EscrowCustomer
from .serializers import UpdateEscrowCustomerSerializer

# Update Customer 
class UpdateCustomerView(APIView):
    permission_classes = [IsAuthenticated]  
    authentication_classes = [JWTAuthentication]  

    def patch(self, request, customer_id):
        serializer = UpdateEscrowCustomerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            payload = {
                "first_name": data.get('first_name'),
                "middle_name": data.get('middle_name', ""),
                "last_name": data.get('last_name'),
                "address": {
                    "line1": data.get('address_line1'),
                    "line2": data.get('address_line2', ""),
                    "city": data.get('city'),
                    "state": data.get('state'),
                    "country": data.get('country'),
                    "post_code": data.get('post_code')
                },
                "phone_number": data.get('phone_number')
            }

            payload = {k: v for k, v in payload.items() if v}

            escrow_url = f'https://api.escrow.com/2017-09-01/customer/{customer_id}'
            email = settings.ESCROW_API_EMAIL
            api_key = settings.ESCROW_API_KEY

            try:
                response = requests.patch(escrow_url, auth=(email, api_key), json=payload)
                response_data = response.json()

                if response.status_code == 200:
                    try:
                        escrow_customer = EscrowCustomer.objects.get(escrow_customer_id=customer_id)
                        escrow_customer.first_name = data.get('first_name', escrow_customer.first_name)
                        escrow_customer.middle_name = data.get('middle_name', escrow_customer.middle_name)
                        escrow_customer.last_name = data.get('last_name', escrow_customer.last_name)
                        escrow_customer.address_line1 = data.get('address_line1', escrow_customer.address_line1)
                        escrow_customer.address_line2 = data.get('address_line2', escrow_customer.address_line2)
                        escrow_customer.city = data.get('city', escrow_customer.city)
                        escrow_customer.state = data.get('state', escrow_customer.state)
                        escrow_customer.country = data.get('country', escrow_customer.country)
                        escrow_customer.post_code = data.get('post_code', escrow_customer.post_code)
                        escrow_customer.phone_number = data.get('phone_number', escrow_customer.phone_number)

                        escrow_customer.save()

                        return Response(response_data, status=status.HTTP_200_OK)
                    except EscrowCustomer.DoesNotExist:
                        return Response({"error": "Customer not found in local database."}, status=status.HTTP_404_NOT_FOUND)

                else:
                    return Response(response_data, status=response.status_code)

            except requests.RequestException as e:
                return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import EscrowTransaction
from .serializers import EscrowTransactionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# class CreateEscrowTransactionView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def post(self, request):
#         # Extract data from the request
#         buyer_email = request.user.email  # Buyer email is taken from the authenticated user
#         seller_email = request.data.get('seller_email')
#         amount = request.data.get('amount')
#         description = request.data.get('description')
#         currency = request.data.get('currency', 'usd')
#         item_title = request.data.get('item_title')
#         item_description = request.data.get('item_description')
#         inspection_period = request.data.get('inspection_period', 259200)  # Default to 3 days
#         # image_url = request.data.get('image_url', '')
#         # merchant_url = request.data.get('merchant_url', '')

#         escrow_payload = {
#             "parties": [
#                 {
#                     "role": "buyer",
#                     "customer": buyer_email,
#                     "initiator": True
#                 },
#                 {
#                     "role": "seller",
#                     "customer": seller_email
#                 }
#             ],
#             "currency": currency,
#             "description": description,
#             "items": [
#                 {
#                     "title": item_title,
#                     "description": item_description,
#                     "type": "domain_name", 
#                     "inspection_period": inspection_period,
#                     "quantity": 1,
#                     "schedule": [
#                         {
#                             "amount": amount,
#                             "payer_customer": buyer_email,
#                             "beneficiary_customer": seller_email
#                         }
#                     ],
#                     # "extra_attributes": {
#                     #     "image_url": image_url,
#                     #     "merchant_url": merchant_url
#                     # }
#                 }
#             ]
#         }

#         escrow_url = 'https://api.escrow.com/2017-09-01/transaction'
#         email = settings.ESCROW_API_EMAIL
#         api_key = settings.ESCROW_API_KEY

#         try:
#             response = requests.post(
#                 escrow_url,
#                 auth=(email, api_key),
#                 json=escrow_payload
#             )

#             response_data = response.json()

#             if response.status_code == 201:
#                 transaction = EscrowTransaction.objects.create(
#                     payer=request.user,
#                     payee_email=seller_email,
#                     amount=amount,
#                     description=description,
#                     status='in_escrow',
#                     escrow_account_id=response_data.get('id')
#                 )

#                 return Response({
#                     "message": "Escrow transaction created successfully.",
#                     "transaction": EscrowTransactionSerializer(transaction).data
#                 }, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(response_data, status=response.status_code)

#         except requests.RequestException as e:
#             return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class CreateEscrowTransactionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        buyer_email = request.data.get('buyer_email')
        seller_email = request.data.get('seller_email')
        amount = request.data.get('amount')
        description = request.data.get('description')
        item_title = request.data.get('item_title')
        item_description = request.data.get('item_description')

        if not buyer_email or not seller_email or not amount:
            return Response({"error": "Buyer email, seller email, and amount are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        escrow_url = 'https://api.escrow.com/2017-09-01/transaction'
        email = settings.ESCROW_API_EMAIL
        api_key = settings.ESCROW_API_KEY

        payload = {
            "parties": [
                {
                    "role": "buyer",
                    "customer": buyer_email,
                    "initiator": True 
                },
                {
                    "role": "seller",
                    "customer": seller_email
                }
            ],
            "currency": "usd",
            "description": description,
            "items": [
                {
                    "title": item_title,
                    "description": item_description,
                    "type": "domain_name",
                    "inspection_period": 259200,
                    "quantity": 1,
                    "schedule": [
                        {
                            "amount": amount,
                            "payer_customer": buyer_email,
                            "beneficiary_customer": seller_email
                        }
                    ],
                    "extra_attributes": {
                        "image_url": "https://i.ebayimg.com/images/g/RicAAOSwzO5e3DZs/s-l1600.jpg",
                        "merchant_url": "https://www.ebay.com"
                    }
                }
            ]
        }

        try:
            response = requests.post(escrow_url, auth=(email, api_key), json=payload)
            response_data = response.json()

            if response.status_code == 201:
                return Response({
                    "message": "Transaction created successfully.",
                    "data": response_data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": "Failed to create transaction.",
                    "details": response_data
                }, status=response.status_code)

        except requests.RequestException as e:
            return Response({
                "error": "Failed to communicate with Escrow API",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Create Transection for Marchent Payment
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Transaction, Schedule, Item, Party
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Replace 'me' with the current user's email
        data = request.data.copy()
        for party in data.get('parties', []):
            if party['customer'] == 'me':
                party['customer'] = request.user.email
                
        for item in data.get('items', []):
            for schedule in item.get('schedule', []):
                if schedule['payer_customer'] == 'me':
                    schedule['payer_customer'] = request.user.email
                if schedule['beneficiary_customer'] == 'me':
                    schedule['beneficiary_customer'] = request.user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)








# # Creating a Excrow Account
# class CreateEscrowCustomerView(APIView):
#     def post(self, request):
#         serializer = EscrowCustomerSerializer(data=request.data)
        
#         if serializer.is_valid():
#             # Extract validated data from the serializer
#             data = serializer.validated_data

#             # Create payload for Escrow API
#             payload = {
#                 "email": data['email'],
#                 "first_name": data['first_name'],
#                 "middle_name": data.get('middle_name', ""),
#                 "last_name": data['last_name'],
#                 "address": {
#                     "line1": data['address_line1'],
#                     "line2": data.get('address_line2', ""),
#                     "city": data['city'],
#                     "state": data['state'],
#                     "country": data['country'],
#                     "post_code": data['post_code']
#                 },
#                 "phone_number": data['phone_number']
#             }

#             # Escrow API endpoint and authentication
#             escrow_url = 'https://api.escrow.com/2017-09-01/customer'
#             email = settings.ESCROW_API_EMAIL  # Store in settings
#             api_key = settings.ESCROW_API_KEY  # Store in settings

#             try:
#                 # Send POST request to Escrow API
#                 response = requests.post(escrow_url, auth=(email, api_key), json=payload)
#                 response_data = response.json()

#                 # Check if the response was successful
#                 if response.status_code == 201:
#                     return Response(response_data, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response(response_data, status=response.status_code)

#             except requests.RequestException as e:
#                 return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CreateEscrowCustomerView(APIView):
#     def post(self, request):
#         serializer = EscrowCustomerSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create Account Escrow 
# Working
# class CreateEscrowCustomerView(APIView):
#     def post(self, request):
#         serializer = EscrowCustomerSerializer(data=request.data)
        
#         if serializer.is_valid():
#             data = serializer.validated_data

#             payload = {
#                 "customer_id": data['customer_id'],
#                 "email": data['email'],
#                 "first_name": data['first_name'],
#                 "middle_name": data.get('middle_name', ""),
#                 "last_name": data['last_name'],
#                 "address": {
#                     "line1": data['address_line1'],
#                     "line2": data.get('address_line2', ""),
#                     "city": data['city'],
#                     "state": data['state'],
#                     "country": data['country'],
#                     "post_code": data['post_code']
#                 },
#                 "phone_number": data['phone_number']
#             }

#             escrow_url = 'https://api.escrow.com/2017-09-01/customer'
#             email = settings.ESCROW_API_EMAIL
#             api_key = settings.ESCROW_API_KEY

#             try:
#                 response = requests.post(escrow_url, auth=(email, api_key), json=payload)
#                 response_data = response.json()

#                 if response.status_code == 201:
#                     escrow_customer = EscrowCustomer.objects.create(
#                         email=data['email'],
#                         first_name=data['first_name'],
#                         middle_name=data.get('middle_name', ""),
#                         last_name=data['last_name'],
#                         address_line1=data['address_line1'],
#                         address_line2=data.get('address_line2', ""),
#                         city=data['city'],
#                         state=data['state'],
#                         country=data['country'],
#                         post_code=data['post_code'],
#                         phone_number=data['phone_number'],
#                         escrow_customer_id=response_data.get('id') 
#                     )
#                     escrow_customer.save()

#                     return Response(response_data, status=status.HTTP_201_CREATED)

#                 else:
#                     return Response(response_data, status=response.status_code)

#             except requests.RequestException as e:
#                 return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CreateEscrowCustomerView(APIView):
#     def post(self, request):
#         serializer = EscrowCustomerSerializer(data=request.data)
        
#         if serializer.is_valid():
#             data = serializer.validated_data

#             payload = {
#                 "email": data['email'],
#                 "first_name": data['first_name'],
#                 "middle_name": data.get('middle_name', ""),
#                 "last_name": data['last_name'],
#                 "address": {
#                     "line1": data['address_line1'],
#                     "line2": data.get('address_line2', ""),
#                     "city": data['city'],
#                     "state": data['state'],
#                     "country": data['country'],
#                     "post_code": data['post_code']
#                 },
#                 "phone_number": data['phone_number']
#             }

#             escrow_url = 'https://api.escrow.com/2017-09-01/customer'
#             email = settings.ESCROW_API_EMAIL
#             api_key = settings.ESCROW_API_KEY

#             try:
#                 response = requests.post(escrow_url, auth=(email, api_key), json=payload)
#                 response_data = response.json()

#                 if response.status_code == 201:
#                     with transaction.atomic():
#                         escrow_customer, created = EscrowCustomer.objects.update_or_create(
#                             defaults={
#                                 'email': data['email'],
#                                 'first_name': data['first_name'],
#                                 'middle_name': data.get('middle_name', ""),
#                                 'last_name': data['last_name'],
#                                 'address_line1': data['address_line1'],
#                                 'address_line2': data.get('address_line2', ""),
#                                 'city': data['city'],
#                                 'state': data['state'],
#                                 'country': data['country'],
#                                 'post_code': data['post_code'],
#                                 'phone_number': data['phone_number'],
#                                 'escrow_customer_id': response_data.get('id')
#                             }
#                         )

#                     status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
#                     return Response(response_data, status=status_code)
#                 else:
#                     return Response(response_data, status=response.status_code)

#             except requests.RequestException as e:
#                 return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CreateEscrowCustomerView(APIView):
#     def post(self, request):
#         serializer = EscrowCustomerSerializer(data=request.data)
        
#         if serializer.is_valid():
#             data = serializer.validated_data

#             # Prepare disbursement_methods for payload
#             disbursement_methods_payload = []
#             for disbursement_method_data in data['disbursement_methods']:
#                 disbursement_methods_payload.append({
#                     "account_name": disbursement_method_data['account_name'],
#                     "account_type": disbursement_method_data['account_type'],
#                     "bank_aba_routing_number": disbursement_method_data['bank_aba_routing_number'],
#                     "bank_account_number": disbursement_method_data['bank_account_number'],
#                     "bank_address": {
#                         "city": disbursement_method_data['bank_address']['city'],
#                         "state": disbursement_method_data['bank_address']['state'],
#                         "country": disbursement_method_data['bank_address']['country']
#                     },
#                     "bank_name": disbursement_method_data['bank_name'],
#                     "currency": disbursement_method_data['currency'],
#                     "type": disbursement_method_data['type']
#                 })

#             payload = {
#                 "email": data['email'],
#                 "first_name": data['first_name'],
#                 "middle_name": data.get('middle_name', ""),
#                 "last_name": data['last_name'],
#                 "address": {
#                     "line1": data['address_line1'],
#                     "line2": data.get('address_line2', ""),
#                     "city": data['city'],
#                     "state": data['state'],
#                     "country": data['country'],
#                     "post_code": data['post_code']
#                 },
#                 "date_of_birth": data['date_of_birth'],
#                 "phone_number": data['phone_number'],
#                 "disbursement_methods": disbursement_methods_payload,
#                 "webhooks": [{
#                     "url": data.get('webhook_url', '')
#                 }]
#             }

#             escrow_url = 'https://api.escrow.com/2017-09-01/customer'
#             email = settings.ESCROW_API_EMAIL
#             api_key = settings.ESCROW_API_KEY

#             try:
#                 response = requests.post(escrow_url, auth=(email, api_key), json=payload)
#                 response_data = response.json()

#                 if response.status_code == 201:
#                     with transaction.atomic():
#                         escrow_customer, created = EscrowCustomer.objects.update_or_create(
#                             email=data['email'],
#                             defaults={
#                                 'first_name': data['first_name'],
#                                 'middle_name': data.get('middle_name', ""),
#                                 'last_name': data['last_name'],
#                                 'address_line1': data['address_line1'],
#                                 'address_line2': data.get('address_line2', ""),
#                                 'city': data['city'],
#                                 'state': data['state'],
#                                 'country': data['country'],
#                                 'post_code': data['post_code'],
#                                 'phone_number': data['phone_number'],
#                                 'escrow_customer_id': response_data.get('id')
#                             }
#                         )

#                         disbursement_methods_data = data['disbursement_methods']
#                         for disbursement_method_data in disbursement_methods_data:
#                             bank_address_data = disbursement_method_data['bank_address']
#                             bank_address = BankAddress.objects.create(
#                                 city=bank_address_data['city'],
#                                 state=bank_address_data['state']
#                             )
#                             DisbursementMethod.objects.create(
#                                 escrow_customer=escrow_customer,
#                                 account_name=disbursement_method_data['account_name'],
#                                 account_type=disbursement_method_data['account_type'],
#                                 bank_aba_routing_number=disbursement_method_data['bank_aba_routing_number'],
#                                 bank_account_number=disbursement_method_data['bank_account_number'],
#                                 bank_address=bank_address,
#                                 bank_name=disbursement_method_data['bank_name'],
#                                 currency=disbursement_method_data['currency'],
#                                 type=disbursement_method_data['type']
#                             )

#                     status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
#                     return Response(response_data, status=status_code)
#                 else:
#                     return Response(response_data, status=response.status_code)

#             except requests.RequestException as e:
#                 return Response({"error": "Failed to communicate with Escrow API", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
