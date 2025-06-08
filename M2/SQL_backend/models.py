from dataclasses import dataclass
from enum import Enum
from datetime import time
from typing import List

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, String, Time, Float, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, composite, relationship

from SQL_backend.db import Base

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



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(String(STRING_LENGTH), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)

    city: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    street: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    zipcode: Mapped[int] = mapped_column(Integer, nullable=False)

    address: Mapped[Address] = composite(Address, city, street, zipcode)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    

class App(Base):
    __tablename__ = "app"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)


class supplier(Base):
    __tablename__ = "supplier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(SqlEnum(VehicleType), nullable=False)


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
    
    dishes: Mapped[List["Dish"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")

class Dish(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[str] = mapped_column(String(STRING_LENGTH), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"), nullable=False)
    restaurant: Mapped["Restaurant"] = relationship(back_populates="disches")


class Order(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurant.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")
    cart: Mapped["Cart"] = relationship(back_populates="order")
    restaurant: Mapped["Restaurant"] = relationship(back_populates="orders")