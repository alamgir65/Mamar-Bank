from django.urls import path
from .views import DepositMoneyView, WithdrawMoneyView, payLoanView, LoanListView, LoanRequestView, TransactionReportView,SendMoneyView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name="deposit_money"),
    path('withdraw/', WithdrawMoneyView.as_view(), name="withdraw_money"),
    path('loan_request/', LoanRequestView.as_view(), name="loan_request"),
    path('loans/', LoanListView.as_view(), name="loan_list"),
    path('pay_loan/<int:loan_id>/', payLoanView.as_view(), name="pay"),
    path('transactions_report/', TransactionReportView.as_view(), name="transaction_report"),
    path('transfer_money/', SendMoneyView.as_view(), name="send_money"),
]
