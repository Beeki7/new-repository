from decimal import Decimal

from django import template

register = template.Library()


def _format_uzs(value: Decimal) -> str:
    try:
        amount = int(Decimal(value))
    except Exception:
        return "0 UZS"
    parts = []
    s = str(amount)
    while s:
        parts.insert(0, s[-3:])
        s = s[:-3]
    return f"{' '.join(parts)} UZS"


@register.filter
def uzs(value):
    """
    Format a numeric value as Uzbek so'm, e.g. 150000 -> "150 000 UZS".
    """
    return _format_uzs(value)

