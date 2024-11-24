"""
 This is a module that define our database schemer
 """

import uuid
from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from website.admin.models.utilities import (
    generate_random_number,
    random_string)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    bind_id = db.Column(
        db.String(36),
        unique=True,
        default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15), unique=True)
    photo_url = db.Column(db.String(150))
    password_hash = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(
        db.DateTime(timezone=True),
        onupdate=func.now())


class UserInfo(db.Model):
    """Model for user info table

    Args:
        db (_type_): _description_
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(
                                'user.bind_id',
                                ondelete='CASCADE'
                            ))
    user = db.relationship(
        'User',
        backref=db.backref('user_info', cascade='all, delete-orphan'))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_bind_id = db.Column(
        db.String(36),
        db.ForeignKey('user.bind_id', ondelete='CASCADE'))
    user = db.relationship(
        'User',
        backref=db.backref('feedbacks', cascade='all, delete-orphan'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    product_item_id = db.Column(
        db.Integer,
        db.ForeignKey('product.item_id', ondelete='CASCADE'))


class Inbox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.Integer, unique=True)
    sender_name = db.Column(db.String(100))
    sender_email = db.Column(db.String(100))
    sender_message = db.Column(db.Text)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket_number = generate_random_number()


class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(36))
    product_item_id = db.Column(
        db.Integer,
        db.ForeignKey('product.item_id', ondelete='CASCADE'))
    product = db.relationship(
        'Product',
        backref=db.backref('shopping_carts', cascade='all, delete-orphan'))
    user_bind_id = db.Column(
        db.String(36),
        db.ForeignKey('user.bind_id', ondelete='CASCADE'))
    user = db.relationship(
        'User',
        backref=db.backref('shopping_carts', cascade='all, delete-orphan'))
    product_qunatity = db.Column(db.Integer)
    product_status = db.Column(db.Enum("paid", "not_paid"), default="not_paid")
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_bind_id = db.Column(
        db.String(36),
        db.ForeignKey('user.bind_id', ondelete='CASCADE'))
    user = db.relationship(
        'User',
        backref=db.backref(
            'transaction_histories', cascade='all, delete-orphan')
        )
    cart_order_no = db.Column(
        db.String(36),
        db.ForeignKey('shopping_cart.order_no', ondelete='CASCADE'))
    shopping_cart = db.relationship(
        'ShoppingCart',
        backref=db.backref(
            'transaction_history', cascade='all, delete-orphan')
        )
    payment_id = db.Column(db.Integer)
    payment_ref = db.Column(db.String(200))
    payment_status = db.Column(db.String(100))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment_id = generate_random_number()
        self.payment_ref = random_string(8)
