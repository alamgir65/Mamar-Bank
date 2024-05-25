from django import forms 
from .models import Transaction,Transfer
from accounts.models import UserAccount
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    

class DepositForm(TransactionForm):
    
    def clean_amount(self):
        min_amount = 100
        amount = self.cleaned_data['amount']
        if amount < min_amount:
            raise forms.ValidationError(f"You can deposite at least {min_amount}")
        return amount

class WithdrawForm(TransactionForm):
    
    def clean_amount(self):
        account = self.account
        min_amount = 500
        max_amount = 50000
        amount = self.cleaned_data['amount']
        balance = account.balance
        if amount > balance:
            raise forms.ValidationError( f"You can withdraw at most {balance}$, You can't withdraw more than your balance")
        if amount< min_amount:
            raise forms.ValidationError(f"You can withdraw at least {min_amount}$")
        if amount > max_amount:
            raise forms.ValidationError(f"You can withdraw at most {max_amount}$")
        
        return amount
    
class LoanRequestForm(TransactionForm):
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount
    
    
class SendMoneyForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    receiver_account_no = forms.IntegerField()
    
    def clean_receiver_account_no(self):
        receiver_account_no = self.cleaned_data.get('receiver_account_no')
        
        if not UserAccount.objects.filter(account_no = receiver_account_no).exists():
            raise forms.ValidationError(f"No account with account no {receiver_account_no}")
        return receiver_account_no