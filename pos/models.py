from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode


class Product(models.Model):
    SIZES = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
    ]

    product_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, choices=SIZES)
    color = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code_image = models.ImageField(upload_to="qrcodes/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.product_id})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate QR code based on product_id if missing
        if self.product_id and not self.qr_code_image:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(self.product_id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"{self.product_id}.png"
            self.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=["qr_code_image"])


class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Sale #{self.id} at {self.created_at:%Y-%m-%d %H:%M}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="sale_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"
