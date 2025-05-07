def format_price(price):
    return f"{price:,} so'm"


def validate_price(price_str):
    try:
        price = float(price_str)
        if price <= 0:
            return False, "Narx musbat bo'lishi kerak"
        return True, price
    except ValueError:
        return False, "Iltimos, faqat raqam kiriting"
