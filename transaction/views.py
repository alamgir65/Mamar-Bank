from django.shortcuts import render,redirect,get_object_or_404
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.generic import CreateView, ListView,FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction,Transfer
from .constants import DEPOSIT,WITHDRAWAL,LOAN,LOANPAID,SENDMONEY
from .forms import TransactionForm,WithdrawForm,DepositForm,LoanRequestForm,SendMoneyForm
from django.contrib import messages
from datetime import datetime, date
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
from accounts.models import UserAccount
from Bank.models import Bank
# Create your views here.

#FOR TRANSACTION EMAIL
def send_transaction_email(request,user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()
        # try:
        #     send_email.send()
        # except:
        #     messages.error(request, "Somthing wrong to send email")

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transaction/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context

    
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )
        
        
    
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        
        # Email send to user for deposite
        send_transaction_email(self.request,self.request.user, amount, "Deposite Message", "transaction/deposite_email.html")
        
            
        return super().form_valid(form)


    

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw'
    
    def get_initial(self):
        initial = {'transaction_type' : WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"{amount}$ withdraw from your account")
        
        #EMail
        
        send_transaction_email(self.request,self.request.user, amount, "Withdrawal Message", "transaction/withdraw_email.html")
        
        return super().form_valid(form)
    
    
class LoanRequestView(TransactionCreateMixin):
    title = 'Loan Request'
    form_class = LoanRequestForm
    
    def get_initial(self):
        initial = {'transaction_type' : LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        loan_count = Transaction.objects.filter(account=self.request.user.account, transaction_type=3, loan_approve=True).count()
        
        if loan_count >= 3:
            return HttpResponse("You already corssed your loan limit.")
        
        messages.success(self.request, f"Your loan request successfully sent to admin.")
        
        return super().form_valid(form)
    
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transaction/transaction_report.html"
    model = Transaction
    balance = 0
    
    def get_queryset(self):
        
        queryset = super().get_queryset().filter(account = self.request.user.account)
        
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
        
        return queryset.distinct()
            
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
    

class payLoanView(LoginRequiredMixin, View):
    
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount <= user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOANPAID
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(self.request, "Loan amount is greater than available balance")
                return redirect('loan_list')



class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transaction/loan_request.html"
    context_object_name = "loans"
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=LOAN)
        return queryset


class SendMoneyView(FormView, LoginRequiredMixin):
    form_class = SendMoneyForm
    template_name = 'transaction/send_money.html'
    success_url = reverse_lazy('home')
    
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({
    #         'account': self.request.user.account
    #     })
    #     return kwargs
    
    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        receiver_account_no = form.cleaned_data['receiver_account_no']
        sender_account = self.request.user.account
        # bank = Bank.objects.get(name="mamar_bank")
        
        try:
            receiver_account = UserAccount.objects.get(account_no=receiver_account_no)
        except UserAccount.DoesNotExist:
            form.add_error('receiver_account_no', "Account does not exist")
            return self.form_invalid(form)
        
        if amount > sender_account.balance:
            form.add_error(None, "Your account balance is not enough")
            return self.form_invalid(form)
        
        sender_account.balance -= amount
        receiver_account.balance += amount
        sender_account.save()
        receiver_account.save()
        
        Transfer.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)
        
        messages.success(self.request, f'Successfully transferred ${amount} to Account No: {receiver_account_no}.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your transfer. Please correct the errors below.')
        return super().form_invalid(form)
        