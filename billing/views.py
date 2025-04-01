from django.utils.timezone import now
from django.shortcuts import render, redirect
from .models import InventoryItem
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from .models import  Invoice,ProductReturn, InvoiceItem
from django.utils.dateparse import parse_date
from .forms import InvoiceForm, InvoiceItemForm
from django.contrib import messages
from django.db.models import Q
from .models import Expense , BusinessInfo
from .forms import ExpenseForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Supplier
from .forms import SupplierForm, InventoryItemForm
from django.contrib.auth.hashers import check_password
from .models import Regitration
from django.contrib.auth import authenticate, login, logout
from datetime import datetime ,  timedelta
import openpyxl
from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import  InvoiceItem
from django.views.generic import ListView
from .models import Invoice
from django.db.models import Sum
from django.views.generic import DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Invoice
from django import forms
from django.contrib.auth import authenticate, login
from datetime import datetime, date




@login_required(login_url='customer_login')
def dashboard(request):
    # 📌 Fetch Business Info
    business_info = BusinessInfo.objects.first()

    # 📌 Total Sales = Sum of `total_amount`
    total_sales = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # 📌 Net Sales (Payable Amount) = Sum of `payable_amount`
    net_sales = Invoice.objects.aggregate(Sum('payable_amount'))['payable_amount__sum'] or 0

    # 📌 Total Expenses = Sum of `amount` from expenses
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    # 📌 Fetch Daily Sales Data (Last 7 Days)
    today = datetime.today().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_sales = {day.strftime('%Y-%m-%d'): 0 for day in last_7_days}

    sales_data_daily = (
        Invoice.objects.filter(date__gte=today - timedelta(days=6))
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('date')
    )

    for entry in sales_data_daily:
        date_str = entry['date'].strftime('%Y-%m-%d')
        daily_sales[date_str] = float(entry['total'])

    daily_labels = list(daily_sales.keys())
    daily_sales_values = list(daily_sales.values())

    # 📌 Fetch Monthly Sales Data (Last 6 Months)
    monthly_sales = (
        Invoice.objects
        .values('date__month')
        .annotate(total=Sum('total_amount'))
        .order_by('date__month')
    )

    month_labels = []
    month_sales_values = []

    for entry in monthly_sales:
        month_name = datetime(2025, entry['date__month'], 1).strftime('%B')
        month_labels.append(month_name)
        month_sales_values.append(float(entry['total']))

    context = {
        'business_info': business_info,  # ✅ Added Business Info
        'total_sales': total_sales,
        'net_sales': net_sales,
        'total_expenses': total_expenses,
        'daily_labels': daily_labels,
        'daily_sales_values': daily_sales_values,
        'month_labels': month_labels,
        'month_sales_values': month_sales_values,
    }
    return render(request, 'dashboard.html', context)


def inventory_management(request):
    # Handle Supplier Form
    if 'supplier_form' in request.POST:
        supplier_form = SupplierForm(request.POST)
        if supplier_form.is_valid():
            supplier_form.save()
            return redirect('inventory_management')
    else:
        supplier_form = SupplierForm()

    # Handle Inventory Item Form
    if 'inventory_form' in request.POST:
        inventory_form = InventoryItemForm(request.POST)
        if inventory_form.is_valid():
            inventory_form.save()
            return redirect('inventory_management')
    else:
        inventory_form = InventoryItemForm()

    # Fetch all suppliers and inventory items
    suppliers = Supplier.objects.all()
    inventory_items = InventoryItem.objects.all()

    context = {
        'supplier_form': supplier_form,
        'inventory_form': inventory_form,
        'suppliers': suppliers,
        'inventory_items': inventory_items,
    }
    return render(request, 'inventory_management.html', context)

def edit_inventory_item(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_management')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'edit_inventory_item.html', {'form': form, 'item': item})


from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Invoice, InvoiceItem, InventoryItem
from .forms import InvoiceForm

def create_invoice(request):
    products = InventoryItem.objects.all()

    if request.method == "POST":
        print("Received POST Data:", request.POST)  # ✅ Debugging

        form = InvoiceForm(request.POST)

        if not form.is_valid():
            messages.error(request, f"❌ Form is invalid: {form.errors}")
            return redirect("create_invoice")

        try:
            with transaction.atomic():  # Ensures data integrity
                invoice = form.save(commit=False)

                # ✅ Capture Payment & Discount Details
                invoice.payment_mode = request.POST.get("payment_mode", "").strip()
                invoice.paid_amount = Decimal(request.POST.get("paid_amount", "0") or 0)
                invoice.discount_amount = Decimal(request.POST.get("discount_amount", "0") or 0)

                # ✅ Save Invoice First (to prevent unsaved object error)
                invoice.total_amount = Decimal(0)  # Temporary value
                invoice.payable_amount = Decimal(0)  # Temporary value
                invoice.balance_amount = Decimal(0)  # Temporary value
                invoice.save()

                # ✅ Retrieve Product Data from Form
                product_ids = request.POST.getlist("product[]")
                quantities = request.POST.getlist("quantity[]")
                prices = request.POST.getlist("price[]")
                gsts = request.POST.getlist("gst[]")
                total_amounts = request.POST.getlist("total_amount[]")

                print("Product IDs:", product_ids)
                print("Quantities:", quantities)
                print("Prices:", prices)  # ✅ Debugging: Ensure prices are received
                print("GSTs:", gsts)
                print("Total Amounts:", total_amounts)

                # ✅ Ensure all required fields are received
                if not all([product_ids, quantities, prices, gsts, total_amounts]):
                    messages.error(request, "❌ Product data is incomplete or mismatched. Please check your inputs.")
                    return redirect("create_invoice")

                # ✅ Deduct Stock Only Once Per Product
                stock_updates = {}

                for i in range(len(product_ids)):
                    product_id = product_ids[i].strip()
                    quantity = int(quantities[i].strip())
                    price = Decimal(prices[i].strip())
                    gst = Decimal(gsts[i].strip())
                    total_amount = Decimal(total_amounts[i].strip())

                    try:
                        product = InventoryItem.objects.get(id=product_id)

                        # ❌ Ensure Sufficient Stock
                        if product.quantity < quantity:
                            messages.warning(request, f"⚠️ Stock insufficient for {product.name}. Available: {product.quantity}")
                            return redirect("create_invoice")

                        # ✅ Accumulate Quantity in Dictionary
                        if product_id in stock_updates:
                            stock_updates[product_id] += quantity  # ✅ SUM Instead of Overwriting
                        else:
                            stock_updates[product_id] = quantity  # ✅ Store First Occurrence

                        # ✅ Create InvoiceItem Entry
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            product=product,
                            quantity=quantity,
                            price=price,
                            gst=gst,
                            total_amount=total_amount
                        )

                        # ✅ Accumulate Total Amount
                        invoice.total_amount += total_amount

                    except InventoryItem.DoesNotExist:
                        messages.error(request, "❌ Selected product does not exist.")
                        return redirect("create_invoice")

                # ✅ Deduct Stock Only Once Per Product (FINAL DEDUCTION HERE)
                for product_id, deducted_qty in stock_updates.items():
                    try:
                        product = InventoryItem.objects.get(id=product_id)
                        print(f"Deducting {deducted_qty} from {product.name} (Before: {product.quantity})")  # ✅ Debugging
                        product.quantity -= deducted_qty
                        product.save()
                        print(f"New stock for {product.name}: {product.quantity}")  # ✅ Debugging
                    except InventoryItem.DoesNotExist:
                        messages.error(request, f"❌ Product with ID {product_id} not found.")

                # ✅ Final Invoice Amount Calculation
                invoice.payable_amount = invoice.total_amount - invoice.discount_amount
                invoice.balance_amount = invoice.payable_amount - invoice.paid_amount
                invoice.save()  # ✅ Save again after updating calculations

                messages.success(request, "✅ Invoice created successfully!")
                return redirect("invoice_list")

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
            return redirect("create_invoice")

    else:
        form = InvoiceForm()

    return render(request, "invoice_form.html", {"form": form, "products": products})



def expenses(request):
    expenses = Expense.objects.all()

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        expenses = expenses.filter(person_name__icontains=search_query)

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Expense added successfully!")
            return redirect('expenses')  # Redirect after saving
        else:
            messages.error(request, "❌ Error: Please check your form!")

    form = ExpenseForm()
    return render(request, 'expenses.html', {'expenses': expenses, 'form': form})



def sales_report(request):
    invoices = Invoice.objects.all()

    # Calculate total values
    total_amount = sum(invoice.total_amount for invoice in invoices)
    payable_amount = sum(invoice.payable_amount for invoice in invoices)
    paid_amount = sum(invoice.paid_amount for invoice in invoices)
    balance_amount = sum(invoice.balance_amount for invoice in invoices)

    context = {
        "invoices": invoices,
        "total_amount": total_amount,
        "payable_amount": payable_amount,
        "paid_amount": paid_amount,
        "balance_amount": balance_amount,
    }
    return render(request, "sales_report.html", context)

def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoice_print.html', {'invoice': invoice})


@csrf_exempt
def customer_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            customer = Regitration.objects.get(username=username)

            if not customer.is_active:
                messages.error(request, "Your account is deactivated. Contact admin.")
                return redirect("customer_login")

            if check_password(password, customer.password):
                request.session["customer_id"] = customer.id  # Store session
                return redirect("dashboard")  # Redirect to dashboard
            else:
                messages.error(request, "Invalid password.")

        except Regitration.DoesNotExist:
            messages.error(request, "Username not found.")

    return render(request, "customer_login.html")
def customer_logout(request):
    logout(request)
    return redirect("customer_login")



class InvoiceListView(ListView):
    model = Invoice
    template_name = "invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return Invoice.objects.all()  # Ensures all invoices are fetched

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch invoices & calculate totals
        invoices = self.get_queryset()
        totals = invoices.aggregate(
            total_amount=Sum("total_amount"),
            payable_amount=Sum("payable_amount"),
            paid_amount=Sum("paid_amount"),
            balance_amount=Sum("balance_amount")
        )

        # Ensure values are not None
        context["total_amount"] = totals["total_amount"] or 0
        context["payable_amount"] = totals["payable_amount"] or 0
        context["paid_amount"] = totals["paid_amount"] or 0
        context["balance_amount"] = totals["balance_amount"] or 0

        return context


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = "invoice_detail.html"
    context_object_name = "invoice"


class InvoiceEditForm(forms.ModelForm):
    pay_due = forms.DecimalField(
        required=False,
        label="Pay Due",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_mobile', 'total_amount', 'payable_amount', 'paid_amount', 'balance_amount']

    def clean_pay_due(self):
        pay_due = self.cleaned_data.get("pay_due", 0)
        if pay_due and pay_due > self.instance.balance_amount:
            raise forms.ValidationError("Pay Due cannot be more than the Balance Amount.")
        return pay_due

    def save(self, commit=True):
        instance = super().save(commit=False)
        pay_due = self.cleaned_data.get("pay_due", 0)

        # Update Paid Amount and Balance Amount
        if pay_due:
            instance.paid_amount += pay_due
            instance.balance_amount -= pay_due

        if commit:
            instance.save()
        return instance


class InvoiceEditView(UpdateView):
    model = Invoice
    form_class = InvoiceEditForm
    template_name = "invoice_edit.html"
    success_url = reverse_lazy('invoice_list')
class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = "invoice_confirm_delete.html"
    success_url = reverse_lazy('invoice_list')


def export_sales_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)

    # Define headers
    writer.writerow(["Invoice ID", "Customer Name", "Mobile No", "Date",
                     "Total Amount", "Payable Amount", "Paid Amount",
                     "Balance Amount", "Payment Mode"])

    # Fetch invoices
    invoices = Invoice.objects.all()

    for invoice in invoices:
        writer.writerow([
            invoice.invoice_id,
            invoice.customer_name,
            invoice.customer_mobile,
            invoice.date,
            f"{invoice.total_amount:.2f}",
            f"{invoice.payable_amount:.2f}",
            f"{invoice.paid_amount:.2f}",
            f"{invoice.balance_amount:.2f}",
            invoice.payment_mode  # Ensure payment mode is included
        ])

    return response


def print_invoice(request, invoice_id):
    invoice = get_object_or_404(
        Invoice.objects.prefetch_related("invoice_items__product"), id=invoice_id
    )
    business = BusinessInfo.objects.first()  # Assuming only one business profile exists

    context = {
        "invoice": invoice,
        "business": business,
    }
    return render(request, "invoice_print.html", context)


def sales_return_view(request):
    invoices = Invoice.objects.all()  # Fetch all invoices
    product_returns = ProductReturn.objects.all()  # Fetch all return records

    context = {
        "invoices": invoices,
        "product_returns": product_returns,
    }
    return render(request, "sales_return.html", context)


def get_invoice_items(request, invoice_id):
    invoice_items = InvoiceItem.objects.filter(invoice_id=invoice_id).select_related("product")
    data = [
        {"id": item.id, "product_name": item.product.name, "quantity": item.quantity}
        for item in invoice_items
    ]
    return JsonResponse(data, safe=False)

def submit_sales_return(request):
    if request.method == "POST":
        invoice_id = request.POST.get("invoiceSelect")
        invoice = get_object_or_404(Invoice, id=invoice_id)

        print("Invoice Selected:", invoice)  # Debugging

        for item in InvoiceItem.objects.filter(invoice=invoice):
            return_quantity = request.POST.get(f"return_quantity_{item.id}")
            if return_quantity:
                return_quantity = int(return_quantity)
                if return_quantity > 0 and return_quantity <= item.quantity:
                    print(f"Saving Product Return for {item.product.name} - Qty: {return_quantity}")  # Debugging

                    # Ensure correct field names are used
                    ProductReturn.objects.create(
                        invoice=invoice,
                        product=item.product,
                        quantity=return_quantity,  # Use 'quantity' if that's the correct field name
                        return_date=now(),
                    )

                    item.quantity -= return_quantity  # Deduct from stock
                    item.save()

        messages.success(request, "Sales Return Processed Successfully!")
        return redirect("sales_return_view")

    return redirect("sales_return_view")




def balance_sheet(request):
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    invoices = Invoice.objects.all()
    expenses = Expense.objects.all()

    if from_date and to_date:
        invoices = invoices.filter(date__range=[from_date, to_date])
        expenses = expenses.filter(date__range=[from_date, to_date])

    daily_data = {}
    running_closing_balance = 0

    for invoice in invoices:
        date = invoice.date.strftime('%Y-%m-%d')
        if date not in daily_data:
            daily_data[date] = {
                'total_sales': 0,
                'cash_collection': 0,
                'upi_collection': 0,
                'total_collection': 0,
                'cash_expense': 0,
                'upi_expense': 0,
                'total_expenses': 0,
                'closing_balance': 0,
                'counter_cash': 0
            }
        daily_data[date]['total_sales'] += invoice.payable_amount
        if invoice.payment_mode == "Cash":
            daily_data[date]['cash_collection'] += invoice.paid_amount
        elif invoice.payment_mode == "UPI":
            daily_data[date]['upi_collection'] += invoice.paid_amount
        daily_data[date]['total_collection'] += invoice.paid_amount

    for expense in expenses:
        date = expense.date.strftime('%Y-%m-%d')
        if date not in daily_data:
            daily_data[date] = {
                'total_sales': 0,
                'cash_collection': 0,
                'upi_collection': 0,
                'total_collection': 0,
                'cash_expense': 0,
                'upi_expense': 0,
                'total_expenses': 0,
                'closing_balance': 0,
                'counter_cash': 0
            }
        if expense.payment_mode == "Cash":
            daily_data[date]['cash_expense'] += expense.amount
        elif expense.payment_mode == "UPI":
            daily_data[date]['upi_expense'] += expense.amount
        daily_data[date]['total_expenses'] += expense.amount

    balance_sheet_data = []

    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        running_closing_balance += data['total_collection'] - data['total_expenses']
        data['closing_balance'] = running_closing_balance
        data['counter_cash'] = data['cash_collection'] - data['cash_expense']  # Counter Cash Calculation
        balance_sheet_data.append({'date': date, **data})

    grand_total_sales = sum(item['total_sales'] for item in balance_sheet_data)
    grand_total_cash_collection = sum(item['cash_collection'] for item in balance_sheet_data)
    grand_total_upi_collection = sum(item['upi_collection'] for item in balance_sheet_data)
    grand_total_collection = sum(item['total_collection'] for item in balance_sheet_data)
    grand_total_cash_expense = sum(item['cash_expense'] for item in balance_sheet_data)
    grand_total_upi_expense = sum(item['upi_expense'] for item in balance_sheet_data)
    grand_total_expenses = sum(item['total_expenses'] for item in balance_sheet_data)
    grand_total_counter_cash = sum(item['counter_cash'] for item in balance_sheet_data)
    final_closing_balance = running_closing_balance

    context = {
        'balance_sheet_data': balance_sheet_data,
        'grand_total_sales': grand_total_sales,
        'grand_total_cash_collection': grand_total_cash_collection,
        'grand_total_upi_collection': grand_total_upi_collection,
        'grand_total_collection': grand_total_collection,
        'grand_total_cash_expense': grand_total_cash_expense,
        'grand_total_upi_expense': grand_total_upi_expense,
        'grand_total_expenses': grand_total_expenses,
        'grand_total_counter_cash': grand_total_counter_cash,
        'final_closing_balance': final_closing_balance,
        'from_date': from_date,
        'to_date': to_date
    }

    return render(request, 'balance_sheet.html', context)