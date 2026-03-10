from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("mahsulotlar/", views.product_list, name="product_list"),
    path("mahsulotlar/yangi/", views.product_create, name="product_create"),
    path("mahsulotlar/<int:pk>/tahrirlash/", views.product_edit, name="product_edit"),
    path("mahsulotlar/<int:pk>/ochirish/", views.product_delete, name="product_delete"),
    path("mahsulotlar/<int:pk>/yorliq/", views.product_label, name="product_label"),
    path("ombor/", views.inventory, name="inventory"),
    path("savdo/", views.checkout, name="checkout"),
    path("api/product/<str:product_id>/", views.api_product_detail, name="api_product_detail"),
    path("api/cart/add", views.api_cart_add, name="api_cart_add"),
    path("api/sale/complete", views.api_sale_complete, name="api_sale_complete"),
]

