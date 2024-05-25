from django.shortcuts import render,redirect
from .forms import UserRegistrationForm,UserUpdateForm
from django.views.generic import FormView,RedirectView
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views import View
# Create your views here.


class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')
    
    def form_valid(self, form):
        user = form.save()
        # print(form.cleaned_data)
        login(self.request, user)
        return super().form_valid(form)
        
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('profile')

# class UserLogoutView(LogoutView):
#     def get_success_url(self):
#         if self.request.user.is_authenticated:
#             logout(self.request)
#         return reverse_lazy('home')
    
class LogoutView(RedirectView):
    url = reverse_lazy('home')  # Redirect to home page after logout

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
    
    
class UserProfileUpdate(View):
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})
    
    