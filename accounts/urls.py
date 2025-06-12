from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/donor/', views.DonorRegistrationView.as_view(), name='register_donor'),
    path('register/org/', views.OrgRegistrationView.as_view(), name='register_org'),
]
