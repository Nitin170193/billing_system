from django.urls import path
from . import views
from django.shortcuts import redirect
from .views import inventory_management,edit_inventory_item,create_invoice
from .views import expenses
from .views import sales_report, customer_login,customer_logout,InvoiceListView,InvoiceDetailView, InvoiceEditView, InvoiceDeleteView
from .views import export_sales_report
from .views import  get_invoice_items,print_invoice
from .views import sales_return_view,submit_sales_return
from .views import balance_sheet

urlpatterns = [
       path('', lambda request: redirect('customer_login'), name='home'),  # Redirect to login page
       path('login/', views.customer_login, name='customer_login'),  # Login view
       path('dashboard/', views.dashboard, name='dashboard'),
       path('inventory/', inventory_management, name='inventory_management'),
       path('inventory/edit/<int:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
       path('invoice/create/', views.create_invoice, name='create_invoice'),
       path("expenses/", expenses, name="expenses"),
       path("sales_report/", sales_report, name="sales_report"),
       path('list/', InvoiceListView.as_view(), name='invoice_list'),
       path('detail/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
       path('edit/<int:pk>/', InvoiceEditView.as_view(), name='invoice_edit'),
       path('delete/<int:pk>/', InvoiceDeleteView.as_view(), name='invoice_delete'),
       path("customer-login/", customer_login, name="customer_login"),
       path("logout/", customer_logout, name="customer_logout"),
       path('export-sales/', export_sales_report, name='export_sales_report'),
       path("sales_return/", sales_return_view, name="sales_return_view"),
       path('get-invoice-items/<int:invoice_id>/', get_invoice_items, name='get_invoice_items'),
       path("print-invoice/<int:invoice_id>/", print_invoice, name="print_invoice"),
       path("submit-sales-return/", submit_sales_return, name="submit_sales_return"),
       path('balance-sheet/', balance_sheet, name='balance_sheet'),


]