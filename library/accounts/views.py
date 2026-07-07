from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from .forms import CustomUserRegisterForm, UserProfileForm
from .models import CustomUser

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

    def get_success_url(self):
        # Redirect based on user role
        user = self.request.user
        if user.is_librarian_or_admin:
            return reverse_lazy('dashboard:admin_dashboard')
        return reverse_lazy('dashboard:member_dashboard')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    model = CustomUser
    form_class = CustomUserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Default role is MEMBER
        user = form.save(commit=False)
        user.role = 'MEMBER'
        user.save()
        messages.success(self.request, "Registration successful! You can now log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please check the details below.")
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update profile. Please verify fields.")
        return super().form_invalid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Password change failed. Please verify your current and new passwords.")
        return super().form_invalid(form)
