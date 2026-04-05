from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Address, Category, Brand, Product, ProductImage, ProductVariant,
    VariantOption, ProductAttribute, Service, Cart, CartItem, Wishlist,
    Order, OrderItem, Payment, Booking, Review, Coupon, 
    NewsletterSubscriber, Page, BlogPost, SiteSetting
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 
                   'email_verified', 'phone_verified', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'email_verified', 'phone_verified', 
                  'gender', 'newsletter_subscribed', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 
                      'birth_date', 'gender')
        }),
        (_('Vérifications et abonnements'), {
            'fields': ('email_verified', 'phone_verified', 'newsletter_subscribed')
        }),
        (_('Adresses'), {
            'fields': ('default_shipping_address', 'default_billing_address'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('last_login',)
        return self.readonly_fields


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'country', 
                   'is_default_shipping', 'is_default_billing', 'created_at')
    list_filter = ('country', 'city', 'is_default_shipping', 'is_default_billing', 'created_at')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name', 
                    'city', 'postal_code', 'street')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


class CategoryInline(admin.TabularInline):
    model = Category
    fields = ('name', 'slug', 'order', 'is_active')
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('parent',)
    inlines = [CategoryInline]
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = _('Nombre de produits')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = _('Nombre de produits')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'is_default')
    readonly_fields = ('created_at',)


class VariantOptionInline(admin.TabularInline):
    model = VariantOption
    extra = 1
    fields = ('name', 'value')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'price', 'compare_price', 'quantity', 'weight')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VariantOptionInline]


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ('name', 'value')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'quantity', 'is_active', 
                   'is_featured', 'published_at', 'created_at')
    list_filter = ('is_active', 'is_featured', 'product_type', 'brand', 
                  'categories', 'published_at', 'created_at')
    search_fields = ('name', 'sku', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    raw_id_fields = ('brand', 'categories')
    inlines = [ProductImageInline, ProductVariantInline, ProductAttributeInline]
    filter_horizontal = ('categories',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'short_description', 'sku')
        }),
        (_('Prix et stock'), {
            'fields': ('price', 'compare_price', 'cost', 'quantity', 
                      'low_stock_threshold', 'track_quantity', 'allow_backorder')
        }),
        (_('Classification'), {
            'fields': ('product_type', 'categories', 'brand')
        }),
        (_('Options'), {
            'fields': ('is_active', 'is_featured', 'requires_shipping', 'weight')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('sku',)
        return self.readonly_fields


# Suppression de la deuxième déclaration de ProductVariantAdmin qui causait l'erreur


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'is_active', 
                   'requires_booking', 'created_at')
    list_filter = ('is_active', 'requires_booking', 'category', 'duration', 'created_at')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('category',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        (_('Détails'), {
            'fields': ('price', 'duration', 'category', 'max_participants')
        }),
        (_('Options'), {
            'fields': ('is_active', 'requires_booking')
        }),
        (_('Image'), {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'service', 'variant', 'quantity', 'price', 'total')
    readonly_fields = ('price', 'total')
    raw_id_fields = ('product', 'service', 'variant')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'items_count', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'items_count', 'total')
    inlines = [CartItemInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'products_count', 'services_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('products', 'services')
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = _('Produits')
    
    def services_count(self, obj):
        return obj.services.count()
    services_count.short_description = _('Services')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'service', 'product_name', 'sku', 'price', 'quantity', 'total')
    readonly_fields = ('product_name', 'sku', 'price', 'quantity', 'total')
    raw_id_fields = ('product', 'service', 'variant')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_method', 'amount', 'status', 'transaction_id', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 
                   'grand_total', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 
                    'shipping_address__first_name', 'shipping_address__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at',
                      'items_total', 'shipping_total', 'tax_total', 
                      'discount_total', 'grand_total')
    raw_id_fields = ('user', 'shipping_address', 'billing_address')
    inlines = [OrderItemInline, PaymentInline]
    
    fieldsets = (
        (None, {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        (_('Adresses'), {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        (_('Totaux'), {
            'fields': ('items_total', 'shipping_total', 'tax_total', 
                      'discount_total', 'grand_total')
        }),
        (_('Livraison'), {
            'fields': ('shipping_method', 'tracking_number'),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'status', 
                   'transaction_id', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'paid_at')
    raw_id_fields = ('order',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'start_time', 'end_time', 
                   'status', 'total', 'created_at')
    list_filter = ('status', 'date', 'service', 'created_at')
    search_fields = ('user__username', 'user__email', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'service')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'service', 'status')
        }),
        (_('Détails de la réservation'), {
            'fields': ('date', 'start_time', 'end_time', 'participants', 'notes')
        }),
        (_('Prix'), {
            'fields': ('price', 'total')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'service', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__username', 'user__email', 'product__name', 'service__name', 'title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'product', 'service')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'service', 'rating', 'is_approved')
        }),
        (_('Contenu'), {
            'fields': ('title', 'comment')
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 
                   'used_count', 'valid_from', 'valid_to')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    filter_horizontal = ('products', 'categories')
    
    fieldsets = (
        (None, {
            'fields': ('code', 'discount_type', 'discount_value', 'is_active')
        }),
        (_('Limites'), {
            'fields': ('minimum_order', 'maximum_discount', 'usage_limit', 'used_count')
        }),
        (_('Validité'), {
            'fields': ('valid_from', 'valid_to')
        }),
        (_('Restrictions'), {
            'fields': ('products', 'categories'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'is_active')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'categories', 'published_at', 'created_at')
    search_fields = ('title', 'excerpt', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    raw_id_fields = ('author',)
    filter_horizontal = ('categories',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content', 'author', 'is_published')
        }),
        (_('Image'), {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        (_('Catégories'), {
            'fields': ('categories',),
            'classes': ('collapse',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'description')
    search_fields = ('key', 'value', 'description')
    
    def value_preview(self, obj):
        if len(obj.value) > 100:
            return f"{obj.value[:100]}..."
        return obj.value
    value_preview.short_description = _('Valeur')