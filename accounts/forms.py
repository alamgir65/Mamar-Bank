from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccount, UserAdress
from .constants import ACCOUNT_TYPE,GENDER_TYPE

class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    city = forms.CharField(max_length=100)
    street_address = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'type' : 'date'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','account_type','password1', 'password2', 'gender', 'city', 'street_address', 'country', 'postal_code', 'birth_date']
        
    def save(self, commit=True):
        tmp_user = super().save(commit=False)
             
        if commit == True:
            tmp_user.save()
            
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')
            country = self.cleaned_data.get('country')
            postal_code = self.cleaned_data.get('postal_code')
            birth_date = self.cleaned_data.get('birth_date')
            
            UserAccount.objects.create(
                user = tmp_user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 100000 + tmp_user.id
            )
            
            UserAdress.objects.create(
                user = tmp_user,
                street_address = street_address,
                city = city,
                country = country,
                postal_code = postal_code,
            )
        return tmp_user
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
            
            
            

class UserUpdateForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    city = forms.CharField(max_length=100)
    street_address = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'type' : 'date'}))
    
    class Meta:
        model=User
        fields = ['first_name', 'last_name', 'email']
        
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
            
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserAccount.DoesNotExist:
                user_account = None
                user_address = None
            
            if user_account:
                self.fields['account_type'].initital = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            user_account , created = UserAccount.objects.get_or_create(user=user)
            user_address , created = UserAdress.objects.get_or_create(user=user)
            
            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()
            
            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()
            
        return user