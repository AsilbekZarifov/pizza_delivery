from database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(70), unique=True)
    password = Column(Text, nullable=True)  #nullable=True parol majburiymas
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user') # one-to many relashionship

    def __repr__(self):
        return f"<user{self.username}"

class Order(Base):

    ORDER_STATUSES = (
        ('PENDING', 'pending'),
        ("IN_TRANSIT", "in_transit"),
        ("DELIVERED", "delivered")
    )

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default='PENDING')
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship('User', back_populates='orders')
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='orders')

    def __repr__(self):
        return f"<order{self.quantity}"


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    orders = relationship('Order', back_populates='product')

    def __repr__(self):
        return f"<product{self.name}"

