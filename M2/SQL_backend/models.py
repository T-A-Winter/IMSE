from dataclasses import dataclass
from enum import Enum
from datetime import time, datetime
from typing import List, Optional

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, String, Time, Float, ForeignKey, DateTime, Boolean, DECIMAL
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, composite, relationship

from db import Base

#TODO: Model not finished yet - NOTE for FKs - might need to embed in other tables 

STRING_LENGTH = 250


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    MOPED = "moped"


@dataclass
class Address():
    city: str
    street: str
    zipcode: int

    def __composite_values__(self):
        return self.city, self.street, self.zipcode
    
    def __eq__(self, other):
        return isinstance(other, Address) and self.__composite_values__() == other.__composite_values__()

    def __ne__(self, other):
        return not self.__eq__(other)

class CartState(Enum):
    OPEN = "open"
    IN_PREPARATION = "in preparation"
    IN_DELIVERY = "in delivery"
    DELIVERED = "delivered"



class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(String(STRING_LENGTH), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(STRING_LENGTH), nullable=False)

    city: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    street: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    zipcode: Mapped[int] = mapped_column(Integer, nullable=False)
    address: Mapped[Address] = composite(Address, city, street, zipcode)

    promo_code: Mapped[Optional[str]] = mapped_column(String(STRING_LENGTH))
    free_delivery: Mapped[bool] = mapped_column(Boolean, default=False)
    cart_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cart.id"))
    invited_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)



class Gast(Base):
    __tablename__ = "gast"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer)
    expiration: Mapped[Optional[time]] = mapped_column(Time)


class PrimeUser(Base):
    __tablename__ = "primeUser"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    fee: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    free_delivery: Mapped[bool] = mapped_column(Boolean, default=True)


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))


class Rating(Base):
    __tablename__ = "rating"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id" , ondelete="CASCADE"), primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id", ondelete="CASCADE"), primary_key=True)
    rating: Mapped[int] = mapped_column(Integer) # TODO: implement validation

class OrderItem(Base):
    __tablename__ = "orderitem"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warenkorb_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="CASCADE"), primary_key=True)
    restaurant_address: Mapped[Optional[str]] = mapped_column(String(255))
    total_price: Mapped[Optional[float]] = mapped_column(DECIMAL(8, 2))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    gericht_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dish.id"))


class App(Base):
    __tablename__ = "app"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class Supplier(Base):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(SqlEnum(VehicleType), nullable=False)
    app_id: Mapped[Optional[int]] = mapped_column(ForeignKey("app.id"))


class Restaurant(Base):
    __tablename__ = "restaurant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    open_from: Mapped[time] = mapped_column(Time, nullable=False)
    open_till: Mapped[time] = mapped_column(Time, nullable=False)


    city: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    street: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    zipcode: Mapped[int] = mapped_column(Integer, nullable=False)
    address: Mapped[Address] = composite(Address, city, street, zipcode)
    dishes: Mapped[List["Dish"]] = relationship(back_populates="restaurant")
    app_id: Mapped[int] = mapped_column(ForeignKey("app.id"))

class Dish(Base):
    __tablename__ = "dish"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    restaurant: Mapped["Restaurant"] = relationship(back_populates="dishes")

class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"))
    state: Mapped[CartState] = mapped_column(SqlEnum(CartState), default=CartState.OPEN, nullable=False)


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("supplier.id"))
    
    # Order details
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    delivery_fee: Mapped[float] = mapped_column(DECIMAL(5, 2), default=3.99)  # Historical delivery fees
    subtotal: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    total: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    
    # Prime status at time of order (historical record)
    was_prime_order: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Order status
    status: Mapped[CartState] = mapped_column(SqlEnum(CartState), default=CartState.IN_PREPARATION)
    
    # Delivery tracking
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    user: Mapped["User"] = relationship(backref="orders")
    restaurant: Mapped["Restaurant"] = relationship(backref="orders")
    cart: Mapped["Cart"] = relationship(backref="order")
    supplier: Mapped[Optional["Supplier"]] = relationship(backref="deliveries")


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"))
    
    # Payment details
    amount: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(SqlEnum(PaymentMethod), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment metadata
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(STRING_LENGTH))
    payment_description: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(backref="payments")
    order: Mapped[Optional["Order"]] = relationship(backref="payment")


class PrimeSubscription(Base):
    __tablename__ = "prime_subscription"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Subscription details
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    monthly_fee: Mapped[float] = mapped_column(DECIMAL(5, 2), default=9.99)
    
    # Subscription status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    cancelled_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(STRING_LENGTH))
    
    # Relationships
    user: Mapped["User"] = relationship(backref="prime_subscription")


class PrimePayment(Base):
    __tablename__ = "prime_payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("prime_subscription.id", ondelete="CASCADE"), nullable=False)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id", ondelete="CASCADE"), nullable=False)
    
    # Prime payment details
    billing_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    billing_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    paid_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    subscription: Mapped["PrimeSubscription"] = relationship(backref="payments")
    payment: Mapped["Payment"] = relationship(backref="prime_payment")