from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('commenter', 'comment_content', 'product', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('commenter', 'comment_content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'publisher', 'price', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('name', 'author')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email')
    list_filter = ('name', 'surname')
    search_fields = ('name', 'surname', 'email')


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('credit_card_number', 'balance')


