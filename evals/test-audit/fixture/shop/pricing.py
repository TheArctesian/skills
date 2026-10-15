def _is_member(customer):
    return customer.get("member", False)


def price(base_pence, customer):
    """Members get 10% off, rounded down to whole pence; never below zero."""
    if base_pence < 0:
        raise ValueError("negative price")
    if _is_member(customer):
        return base_pence * 9 // 10
    return base_pence


def format_price(p):
    return f"£{p / 100:.2f}"
