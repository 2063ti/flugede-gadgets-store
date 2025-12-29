from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, ProductSpecification,
    UserProfile, Address, Cart, CartItem, Wishlist, Coupon,
    Order, OrderItem, OrderStatusHistory, ReturnRequest,
    Review, ReviewImage, Newsletter, ContactMessage
)


# Inline Admin Classes
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary')


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3
    fields = ('name', 'value', 'order')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'total_price')
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'notes', 'created_at')
    can_delete = False


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_price', 'stock', 'stock_status_badge', 'is_active', 'is_featured')
    list_filter = ('category', 'brand', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'discount_price', 'stock', 'is_active', 'is_featured')
    inlines = [ProductImageInline, ProductSpecificationInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'brand', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_active', 'is_featured')
        }),
        ('Additional Info', {
            'fields': ('warranty_period',)
        }),
    )

    def stock_status_badge(self, obj):
        status = obj.stock_status
        if status == 'Out of Stock':
            color = 'red'
        elif status == 'Low Stock':
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status_badge.short_description = 'Stock Status'


# Product Image Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'image_preview', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'


# User Profile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'address_type', 'is_default')
    list_filter = ('address_type', 'is_default', 'state')
    search_fields = ('user__username', 'full_name', 'city', 'state', 'pincode')


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items_display', 'subtotal_display', 'created_at')
    search_fields = ('user__username',)

    def total_items_display(self, obj):
        return obj.total_items
    total_items_display.short_description = 'Total Items'

    def subtotal_display(self, obj):
        return f"₹{obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'


# Cart Item Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price_display')
    search_fields = ('cart__user__username', 'product__name')

    def total_price_display(self, obj):
        return f"₹{obj.total_price}"
    total_price_display.short_description = 'Total Price'


# Wishlist Admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')


# Coupon Admin
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'usage_limit', 'used_count', 'is_active', 'is_valid_badge')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    list_editable = ('is_active',)

    def is_valid_badge(self, obj):
        is_valid = obj.is_valid()
        color = 'green' if is_valid else 'red'
        text = 'Valid' if is_valid else 'Invalid'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    is_valid_badge.short_description = 'Status'


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'order_status', 'payment_status', 'payment_method', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'address')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_charge', 'tax', 'discount', 'total', 'coupon')
        }),
        ('Status', {
            'fields': ('order_status', 'payment_method', 'payment_status')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'expected_delivery_date', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('order_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if change:  # If updating existing order
            old_status = Order.objects.get(pk=obj.pk).order_status
            if old_status != obj.order_status:
                # Create status history
                OrderStatusHistory.objects.create(
                    order=obj,
                    status=obj.order_status,
                    notes=f"Status changed from {old_status} to {obj.order_status}"
                )
        super().save_model(request, obj, form, change)


# Return Request Admin
@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('user__username', 'order_item__order__order_number')
    readonly_fields = ('created_at', 'updated_at')


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    list_editable = ('is_approved',)
    inlines = [ReviewImageInline]


# Newsletter Admin
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    list_editable = ('is_active',)


# Contact Message Admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
