from django.urls import path

from .views import pages, api

urlpatterns = [
    path("", pages.dashboard, name="dashboard"),
    path("mahsulotlar/", pages.product_list, name="product_list"),
    path("mahsulotlar/yangi/", pages.product_create, name="product_create"),
    path("mahsulotlar/<int:pk>/tahrirlash/", pages.product_edit, name="product_edit"),
    path("mahsulotlar/<int:pk>/ochirish/", pages.product_delete, name="product_delete"),
    path("mahsulotlar/<int:pk>/yorliq/", pages.product_label, name="product_label"),
    path("ombor/", pages.inventory, name="inventory"),
    path("savdo/", pages.checkout, name="checkout"),
    path("pos/scan/", pages.pos_scan, name="pos_scan"),
    path("api/product/<str:product_id>/", api.api_product_detail, name="api_product_detail"),
    path("api/cart/add", api.api_cart_add, name="api_cart_add"),
    path("api/sale/complete", api.api_sale_complete, name="api_sale_complete"),
]

