""" This is the module that define the schiemer for the admin """

import uuid
from website import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from website.admin.models.utilities import generate_random_number


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    bind_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    working_status = db.Column(db.Enum('working', 'suspended', 'pending', 'not_working'), default="pending")
    admin_office = db.Column(db.Enum('super_admin', 'admin', 'product_manager', 'social_manager'))
    photo_url = db.Column(db.String(150))
    password_hash = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, unique=True)
    product_category = db.Column(db.Enum(
        'vehicles',
        'fashion&lifestyle',
        'teddy_bears',
        'food&beverages',
        'electronics&technology',
        'indurial&suuplies',
        'agriculture&agro_allied',
        'constructed&real_estate',
        'energy_solution',
        'oil&gas',
        'fruits&veges'))
    product_title = db.Column(db.String(100))
    product_image = db.Column(db.String(100), nullable=True)
    product_des = db.Column(db.Text)
    product_price = db.Column(db.Integer)
    market_status = db.Column(db.Enum('Available', 'Unavailable'), default="Available")
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id = generate_random_number()


