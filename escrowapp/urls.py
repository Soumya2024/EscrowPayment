from django.urls import path
from .views import CreateEscrowTransactionView
from .views import CreateEscrowCustomerView
from .views import UpdateCustomerView
from .views import RegistrationView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# urlpatterns = [
#     path('api/escrow/initiate/', InitiateEscrowPayment.as_view(), name='initiate_escrow'),
# ]


urlpatterns = [
    # path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('escrow/transaction/', CreateEscrowTransactionView.as_view(), name='initiate_escrow'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-customer/', CreateEscrowCustomerView.as_view(), name='create_customer'),
    path('update-customer/<int:customer_id>/', UpdateCustomerView.as_view(), name='update-customer')
]
