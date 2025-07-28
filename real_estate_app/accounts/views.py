from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView, View, FormView, UpdateView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import User
from .forms import (
    CustomerRegistrationForm, AgentRegistrationForm, CustomLoginForm, 
    KeyBasedPasswordResetForm, ProfileUpdateForm
)
from .utils import validate_email_domain

@login_required
def favorites(request):
    """
    Redirect to the properties favorites list
    """
    return redirect('properties:favorites_list')

class CustomerRegistrationView(CreateView):
    model = User
    form_class = CustomerRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'customer'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Registration successful! You can now login with your credentials."
        )
        return response

class AgentRegistrationView(CreateView):
    model = User
    form_class = AgentRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'agent'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Registration successful! You can now login with your credentials."
        )
        return response

class LoginView(FormView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.username}!")
            next_url = self.request.GET.get('next', None)
            if next_url:
                return redirect(next_url)
            return super().form_valid(form)
        return self.form_invalid(form)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

class ForgotPasswordView(FormView):
    template_name = 'accounts/forgot_password.html'
    form_class = KeyBasedPasswordResetForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        unique_key = form.cleaned_data['unique_key']
        new_password = form.cleaned_data['new_password']
        
        try:
            user = User.objects.get(unique_key=unique_key)
            user.set_password(new_password)
            user.save()
            messages.success(self.request, "Password has been reset successfully.")
            return super().form_valid(form)
        except User.DoesNotExist:
            messages.error(self.request, "Invalid unique key. Please try again.")
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, 'accounts/profile.html', {'user': request.user})

@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your profile has been updated successfully.")
        return response