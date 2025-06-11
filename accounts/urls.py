from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/donor/', views.DonorRegistrationView.as_view(), name='register_donor'),
]
