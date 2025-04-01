from django.contrib import admin
from .models import Supplier, InventoryItem, Customer, Invoice
from .models import Regitration
from django.contrib.auth.hashers import make_password
from .models import BusinessInfo

admin.site.register(BusinessInfo)
# Supplier Admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_number", "email", "gstin")
    search_fields = ("name", "contact_number", "email", "gstin")

# Inventory Item Admin
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier", "quantity", "price", "gst_percentage", "created_at")
    search_fields = ("name", "supplier__name")
    list_filter = ("supplier", "created_at")

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("C_name", "mobile_no", "gst_no", "address")
    search_fields = ("C_name", "mobile_no", "gst_no")

# FIXED Invoice Admin
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_id', 'customer_name', 'customer_mobile', 'gst_no',
        'total_amount', 'discount_amount', 'payable_amount',
        'paid_amount', 'balance_amount', 'date', 'payment_mode'
    )
    search_fields = ('invoice_id', 'customer_name', 'customer_mobile')
    list_filter = ('date', 'balance_amount', 'payment_mode')


admin.site.register(Invoice, InvoiceAdmin)

class RegitrationAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "mobile", "is_active")
    list_editable = ("is_active",)  # Admin can activate/deactivate users
    readonly_fields = ("created_at",)  # Prevent modification of creation date
    fieldsets = (
        ("Customer Info", {"fields": ("username", "name", "email", "mobile", "address", "gst_number")}),
        ("Security", {"fields": ("password",)}),
        ("Status", {"fields": ("is_active", "created_at")}),
    )

    def save_model(self, request, obj, form, change):
        if "password" in form.changed_data:
            obj.password = make_password(obj.password)  # Hash password before saving
        super().save_model(request, obj, form, change)

admin.site.register(Regitration, RegitrationAdmin)

