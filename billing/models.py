import uuid
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import  transaction
from decimal import Decimal


class BusinessInfo(models.Model):
    name = models.CharField(max_length=255, default="My Business")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    address = models.TextField(default="Not Provided")
    contact = models.CharField(max_length=15 , default="0000000000")
    gst_no = models.CharField(max_length=50 ,default="N/A")
    email = models.EmailField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=255)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        gst_amount = (self.price * self.gst_percentage) / 100
        return self.quantity * (self.price + gst_amount)

    def __str__(self):
        return self.name

class Customer(models.Model):
    C_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    gst_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.C_name

class Invoice(models.Model):
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
    ]
    invoice_id = models.CharField(max_length=20, unique=True, editable=False, default=None)
    customer_name = models.CharField(max_length=255)
    customer_mobile = models.CharField(max_length=10)
    gst_no = models.CharField(max_length=20, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    date = models.DateField(default=now, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = "INV-" + str(uuid.uuid4().hex[:8]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.customer_name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey("Invoice", related_name="invoice_items", on_delete=models.CASCADE)
    product = models.ForeignKey("InventoryItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        with transaction.atomic():  # Ensures safe stock updates
            if not self.pk:  # New InvoiceItem
                if self.product.quantity < self.quantity:
                    raise ValueError(f"❌ Insufficient stock for {self.product.name}. Available: {self.product.quantity}")
                self.product.quantity -= self.quantity
            else:  # Updating existing InvoiceItem
                old_item = InvoiceItem.objects.get(pk=self.pk)
                quantity_difference = self.quantity - old_item.quantity

                if quantity_difference > 0:  # Increased quantity
                    if self.product.quantity < quantity_difference:
                        raise ValueError(f"❌ Not enough stock for {self.product.name}. Available: {self.product.quantity}")
                    self.product.quantity -= quantity_difference
                elif quantity_difference < 0:  # Decreased quantity
                    self.product.quantity += abs(quantity_difference)

            # Calculate GST and Total Amount
            gst_amount = (self.price * self.quantity * self.gst) / 100
            self.total_amount = (self.price * self.quantity) + gst_amount

            self.product.save()  # Save updated stock
            super().save(*args, **kwargs)  # Save InvoiceItem

    def __str__(self):
        return f"{self.product.name} - Invoice {self.invoice.invoice_id}"

class Expense(models.Model):
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
    ]

    date = models.DateField(default=now)  # Auto set date when saved
    person_name = models.CharField(max_length=100)
    reference_person = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='Cash')

    def __str__(self):
        return f"{self.person_name} - ₹{self.amount} ({self.payment_mode})"

class Regitration(models.Model):
    username = models.CharField(max_length=150, unique=True)  # Unique username
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)  # Store hashed password
    is_active = models.BooleanField(default=True)  # Activation field
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)  # Hash password
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class ProductReturn(models.Model):
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="product_returns")
    product = models.ForeignKey("InventoryItem", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    return_reason = models.TextField(blank=True, null=True)
    return_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return: {self.product.name} ({self.quantity})"