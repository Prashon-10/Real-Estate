from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/customer/', views.CustomerRegistrationView.as_view(), name='register_customer'),
    path('register/agent/', views.AgentRegistrationView.as_view(), name='register_agent'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
]