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
    name = models.CharField("Nomi", max_length=200)
    price = models.DecimalField("Narx (UZS)", max_digits=12, decimal_places=2)
    size = models.CharField("O'lcham", max_length=10, choices=SIZES, blank=True, default="")
    color = models.CharField("Rang", max_length=50)
    quantity = models.PositiveIntegerField("Miqdor (ombor)", default=0)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    # QR code image stored on disk; encoded value is product_id
    qr_code = models.ImageField("QR kod", upload_to="qrcodes/", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.product_id})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.product_id and not self.qr_code:
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
            self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=["qr_code"])


class Sale(models.Model):
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    total_amount = models.DecimalField(
        "Umumiy summa (UZS)", max_digits=14, decimal_places=2, default=0
    )

    def __str__(self) -> str:
        return f"Sale #{self.id} at {self.created_at:%Y-%m-%d %H:%M}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="sale_items", on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField("Soni")
    price = models.DecimalField("Narx (UZS)", max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField("Vaqt", auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"
