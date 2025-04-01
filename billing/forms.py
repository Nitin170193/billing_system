from django import forms
from .models import Supplier, InventoryItem
from .models import Invoice, InvoiceItem, InventoryItem, Customer


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_number', 'email', 'address', 'gstin']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gstin': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem

        fields = ['name', 'supplier', 'quantity', 'price', 'gst_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'gst_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }


from django import forms
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'
        widgets = {
            'customer_mobile': forms.TextInput(attrs={'maxlength': '10'}),
            'gst_no': forms.TextInput(attrs={'placeholder': 'Enter GST No (Optional)'}),  # Optional GST
            'total_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'balance_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'payment_mode': forms.TextInput(),
        }

    # Make fields optional
    customer_mobile = forms.CharField(required=False)
    gst_no = forms.CharField(required=False)  # ✅ GST Number is now optional
    total_amount = forms.DecimalField(required=False)
    discount_amount = forms.DecimalField(required=False)
    balance_amount = forms.DecimalField(required=False)
    payment_mode = forms.CharField(required=False)

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'price', 'gst', 'total_amount']

from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['person_name', 'reference_person', 'reason', 'amount', 'payment_mode']

    # Custom styling for Bootstrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control border-primary shadow-sm'})
