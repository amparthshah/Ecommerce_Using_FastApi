from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, orm
from sqlalchemy.sql import func
from .database import Base


class UserRoles(Base):
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    user_role = Column(Integer, ForeignKey('user_roles.id', ondelete="SET DEFAULT"), default=3)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    image = Column(String, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")


class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey('products.id', ondelete="CASCADE"))
    quantity = Column(Integer)
    total = Column(Float, nullable=False)
    product = relationship("Product", back_populates="carts")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def calculate_total(self):
        product = self.product
        if product:
            return product.price * self.quantity
        else:
            return 0.0

    # Update the total field when the quantity or product changes
    @orm.reconstructor
    def init_on_load(self):
        self.total = self.calculate_total

    # Update the total field when the quantity or product changes
    @orm.validates('quantity', 'product')
    def update_total(self, key, value):
        self.total = self.calculate_total
        return value


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow())
    
class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'))
    order = relationship("Order", backref="order_items")
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))
    product = relationship("Product", backref="order_items")
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
