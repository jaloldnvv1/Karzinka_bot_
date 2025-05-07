class Product:
    id: int
    name: str
    price: float
    category: str


class CartItem:
    id: int
    user_id: int
    product_id: int
    quantity: int


class Admin:
    user_id: int
