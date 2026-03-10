from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Sale, SaleItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_id", "size", "color", "price", "quantity_colored")
    search_fields = ("name", "product_id", "color")
    list_filter = ("size", "color")
    list_editable = ("price",)
    ordering = ("name",)

    def quantity_colored(self, obj):
        if obj.quantity == 0:
            color = "#b91c1c"
            label = "0 (tugagan)"
        elif obj.quantity < 5:
            color = "#b45309"
            label = f"{obj.quantity} (kam qoldi)"
        else:
            color = "#15803d"
            label = str(obj.quantity)
        return format_html('<span style="font-weight:600;color:{};">{}</span>', color, label)

    quantity_colored.short_description = "Ombordagi miqdor"


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "timestamp")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total_amount")
    date_hierarchy = "created_at"
    inlines = [SaleItemInline]
    ordering = ("-created_at",)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("sale", "product", "quantity", "price", "timestamp")
    search_fields = ("product__name", "product__product_id")
    list_filter = ("product__size", "product__color")

from django.contrib import admin

# Register your models here.
