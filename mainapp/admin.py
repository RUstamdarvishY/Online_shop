from django.contrib import admin
from mainapp.models import Collection, Product, Customer, Cart, CartItem, Order, OrderItem, Address


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    list_display = ['title', 'unit_price']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    list_display = ['title']
    search_fields = ['title']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    list_per_page = 5
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer', 'payment_status']
    list_editable = ['payment_status']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['created_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity']


@admin.register(Address)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['street', 'house']