from django.contrib import admin
from .models import Manufacturer, ProductType, Product


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    search_fields = ['name', 'country']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'product_type', 'created_at', 'slug']
    list_filter = ['manufacturer', 'product_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'manufacturer', 'product_type', 'description')
        }),
        ('Изображение', {
            'fields': ('image',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )
