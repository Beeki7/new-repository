from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.product_list, name="product_list"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/<int:pk>/label/", views.product_label, name="product_label"),
    path("checkout/", views.checkout, name="checkout"),
    path("api/product/<str:product_id>/", views.api_get_product_by_code, name="api_get_product_by_code"),
    path("api/complete-sale/", views.api_complete_sale, name="api_complete_sale"),
]

