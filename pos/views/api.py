import json

from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import Product, Sale, SaleItem


def api_product_detail(request: HttpRequest, product_id: str) -> JsonResponse:
    product = get_object_or_404(Product, product_id=product_id)
    data = {
        "id": product.id,
        "product_id": product.product_id,
        "name": product.name,
        "price": float(product.price),
        "size": product.size,
        "color": product.color,
        "quantity": product.quantity,
    }
    return JsonResponse(data)


@csrf_exempt
def api_cart_add(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Faqat POST ruxsat etilgan"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        product_id = payload.get("product_id", "").strip()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Yaroqsiz ma'lumot"}, status=400)

    if not product_id:
        return JsonResponse({"error": "Mahsulot ID kiritilmagan"}, status=400)

    product = get_object_or_404(Product, product_id=product_id)
    if product.quantity <= 0:
        return JsonResponse({"error": "Bu mahsulot omborda yo'q"}, status=400)

    data = {
        "id": product.id,
        "product_id": product.product_id,
        "name": product.name,
        "price": float(product.price),
        "size": product.size,
        "color": product.color,
        "quantity": product.quantity,
    }
    return JsonResponse(data)


@csrf_exempt
def api_sale_complete(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Faqat POST ruxsat etilgan"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        items = payload.get("items", [])
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Yaroqsiz ma'lumot"}, status=400)

    if not items:
        return JsonResponse({"error": "Savatcha bo'sh"}, status=400)

    sale = Sale.objects.create()
    total_amount = 0

    for item in items:
        product_id = item.get("product_id")
        quantity = int(item.get("quantity", 1))
        product = get_object_or_404(Product, product_id=product_id)

        if quantity <= 0:
            continue

        if product.quantity < quantity:
            return JsonResponse(
                {"error": f"{product.name} uchun omborda yetarli mahsulot yo'q"},
                status=400,
            )

        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            price=product.price,
        )

        total_amount += float(sale_item.price) * sale_item.quantity

        product.quantity -= quantity
        product.save(update_fields=["quantity"])

    sale.total_amount = total_amount
    sale.save(update_fields=["total_amount"])

    return JsonResponse(
        {"status": "ok", "sale_id": sale.id, "total_amount": total_amount}
    )

