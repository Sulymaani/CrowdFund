from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/donor/', views.DonorRegistrationView.as_view(), name='register_donor'),
    path('register/org/', views.OrgRegistrationView.as_view(), name='register_org'),
    path('dashboard/', views.DonorDashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
]
