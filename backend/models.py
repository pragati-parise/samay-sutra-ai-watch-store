from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120)); email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255)); address: Mapped[str] = mapped_column(Text, default=""); contact_number: Mapped[str] = mapped_column(String(30), default="")
    is_admin: Mapped[bool] = mapped_column(default=False); cart: Mapped["Cart | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
class Category(Base):
    __tablename__ = "categories"; id: Mapped[int] = mapped_column(primary_key=True); name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    products: Mapped[list["Product"]] = relationship(back_populates="category")
class Product(Base):
    __tablename__ = "products"; id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True); brand: Mapped[str] = mapped_column(String(100), index=True); category_id: Mapped[int] = mapped_column(ForeignKey("categories.id")); price: Mapped[float] = mapped_column(Numeric(10, 2)); image: Mapped[str] = mapped_column(String(500)); description: Mapped[str] = mapped_column(Text); stock: Mapped[int] = mapped_column(Integer, default=20); strap: Mapped[str] = mapped_column(String(60), default="Leather"); color: Mapped[str] = mapped_column(String(60), default="Black")
    category: Mapped[Category] = relationship(back_populates="products"); reviews: Mapped[list["Review"]] = relationship(back_populates="product", cascade="all, delete-orphan")
class Cart(Base):
    __tablename__ = "carts"; id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped[User] = relationship(back_populates="cart"); items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")
class CartItem(Base):
    __tablename__ = "cart_items"; __table_args__ = (UniqueConstraint("cart_id", "product_id"),); id: Mapped[int] = mapped_column(primary_key=True); cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id")); product_id: Mapped[int] = mapped_column(ForeignKey("products.id")); quantity: Mapped[int] = mapped_column(default=1)
    cart: Mapped[Cart] = relationship(back_populates="items"); product: Mapped[Product] = relationship()
class WishlistItem(Base):
    __tablename__ = "wishlist_items"; __table_args__ = (UniqueConstraint("user_id", "product_id"),); id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("users.id")); product_id: Mapped[int] = mapped_column(ForeignKey("products.id")); product: Mapped[Product] = relationship()
class Order(Base):
    __tablename__ = "orders"; id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("users.id")); total: Mapped[float] = mapped_column(Numeric(10, 2)); status: Mapped[str] = mapped_column(String(40), default="Placed"); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
class OrderItem(Base):
    __tablename__ = "order_items"; id: Mapped[int] = mapped_column(primary_key=True); order_id: Mapped[int] = mapped_column(ForeignKey("orders.id")); product_id: Mapped[int] = mapped_column(ForeignKey("products.id")); quantity: Mapped[int] = mapped_column(); price: Mapped[float] = mapped_column(Numeric(10, 2))
    order: Mapped[Order] = relationship(back_populates="items"); product: Mapped[Product] = relationship()
class Review(Base):
    __tablename__ = "reviews"; __table_args__ = (UniqueConstraint("user_id", "product_id"),); id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[int] = mapped_column(ForeignKey("users.id")); product_id: Mapped[int] = mapped_column(ForeignKey("products.id")); rating: Mapped[int] = mapped_column(); comment: Mapped[str] = mapped_column(Text, default=""); created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    product: Mapped[Product] = relationship(back_populates="reviews")
