from datetime import timedelta
import json

from django.db.models import Sum, F
from django.db.models.functions import TruncDate
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import Product, SaleItem

LOW_STOCK_THRESHOLD = 5


def dashboard(request: HttpRequest) -> HttpResponse:
    now = timezone.now()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - timedelta(days=7)
    start_of_month = start_of_today - timedelta(days=30)
    start_of_year = start_of_today - timedelta(days=365)

    revenue_qs = SaleItem.objects.annotate(total=F("price") * F("quantity"))

    def revenue_since(start):
        return (
            revenue_qs.filter(timestamp__gte=start).aggregate(total=Sum("total"))["total"]
            or 0
        )

    daily_revenue = revenue_since(start_of_today)
    weekly_revenue = revenue_since(start_of_week)
    monthly_revenue = revenue_since(start_of_month)
    yearly_revenue = revenue_since(start_of_year)

    total_products_sold = (
        SaleItem.objects.aggregate(units=Sum("quantity"))["units"] or 0
    )

    best_selling_products = (
        Product.objects.annotate(total_sold=Sum("sale_items__quantity"))
        .filter(total_sold__gt=0)
        .order_by("-total_sold")[:10]
    )
    top_labels = [p.name for p in best_selling_products]
    top_values = [int(p.total_sold or 0) for p in best_selling_products]

    low_stock_products = Product.objects.filter(quantity__lte=LOW_STOCK_THRESHOLD)

    last_14_days = now - timedelta(days=14)
    daily_series_qs = (
        revenue_qs.filter(timestamp__gte=last_14_days)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(total=Sum("total"))
        .order_by("day")
    )
    daily_labels = [p["day"].strftime("%d.%m") for p in daily_series_qs]
    daily_values = [float(p["total"]) for p in daily_series_qs]

    context = {
        "daily_revenue": daily_revenue,
        "weekly_revenue": weekly_revenue,
        "monthly_revenue": monthly_revenue,
        "yearly_revenue": yearly_revenue,
        "total_products_sold": total_products_sold,
        "best_selling_products": best_selling_products,
        "low_stock_products": low_stock_products,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "daily_labels_json": json.dumps(daily_labels),
        "daily_values_json": json.dumps(daily_values),
        "top_labels_json": json.dumps(top_labels),
        "top_values_json": json.dumps(top_values),
    }
    return render(request, "pos/dashboard.html", context)


def product_list(request: HttpRequest) -> HttpResponse:
    products = Product.objects.all().order_by("name")
    return render(
        request,
        "pos/product_list.html",
        {"products": products, "low_stock_threshold": LOW_STOCK_THRESHOLD},
    )


def inventory(request: HttpRequest) -> HttpResponse:
    products = Product.objects.all().order_by("name")
    return render(
        request,
        "pos/inventory.html",
        {"products": products, "low_stock_threshold": LOW_STOCK_THRESHOLD},
    )


def product_create(request: HttpRequest) -> HttpResponse:
    sizes = Product.SIZES
    if request.method == "POST":
        product_id = request.POST.get("product_id", "").strip()
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price") or "0"
        size = request.POST.get("size", "").strip()
        color = request.POST.get("color", "").strip()
        quantity = request.POST.get("quantity") or "0"

        if product_id and name:
            Product.objects.create(
                product_id=product_id,
                name=name,
                price=price,
                size=size,
                color=color,
                quantity=quantity,
            )
            return redirect("product_list")

    return render(request, "pos/product_form.html", {"product": None, "sizes": sizes})


def product_edit(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    sizes = Product.SIZES
    if request.method == "POST":
        product.product_id = request.POST.get("product_id", "").strip()
        product.name = request.POST.get("name", "").strip()
        product.price = request.POST.get("price") or product.price
        product.size = request.POST.get("size", "").strip()
        product.color = request.POST.get("color", "").strip()
        product.quantity = request.POST.get("quantity") or product.quantity
        product.save()
        return redirect("product_list")

    return render(request, "pos/product_form.html", {"product": product, "sizes": sizes})


def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "pos/product_confirm_delete.html", {"product": product})


def product_label(request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    if not product.qr_code:
        product.save()
    return render(request, "pos/product_label.html", {"product": product})


def checkout(request: HttpRequest) -> HttpResponse:
    # legacy route (/savdo/) kept for backwards compatibility
    return render(request, "pos/checkout.html")


def pos_scan(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "pos/scan.html",
        {"low_stock_threshold": LOW_STOCK_THRESHOLD},
    )

