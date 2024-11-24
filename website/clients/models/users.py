""" This is a modue that deals with the functionality of the user """

import uuid
import re
import random
from website import db
from website.clients.models.models import User, ShoppingCart, UserInfo
from website.admin.models.models import Product
from website.clients.models.utils import generate_order_no, send_email
from website.admin.models.admins import get_order_key, get_total_amt
# from website.admin.models.utilities import generate_random_number


# vaildate user info if it is an email or a phone number
def validate_email(email):
    # Regular expression pattern for validating email addresses
    email_pattern = r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_pattern, email) is not None


def validate_phone_number(phone_number):
    # Regular expression pattern for validating phone numbers
    phone_pattern = (
        r'^(\+?\d{1,3})?[-.\s]?\(?\d{3}\)?'
        r'[-.\s]?\d{3}[-.\s]?\d{4}$'
    )
    return re.match(phone_pattern, phone_number) is not None


# Fetching a user data thorogh their email address
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


# Fetching a user data through their phone number
def get_user_by_phone_number(phone_number):
    return User.query.filter_by(phone_number=phone_number).first()


# Fetching the user data through their session bind_id
def get_user_by_bind_id(bind_id):
    """ This is a function that return the user data as a dictionary """
    return User.query.filter_by(bind_id=bind_id).first()


def get_user_info_by_bind_id(bind_id):
    """ This is a function that return the user data as a dictionary """
    return UserInfo.query.filter_by(user_id=bind_id).first()


def fetch_eight_new_products():
    """ This function fetch 8 newly uploaded products """
    return Product.query.order_by(Product.create_date.desc()).limit(8).all()


def fetch_all_products():
    """ This is a function that return all the uploaded products in the
        database
    """
    return Product.query.order_by(Product.create_date.desc()).all()


def shuffle_list(products):
    """Shuffle a list of products."""
    shuffled_products = list(products)  # Ensure it's a list, not a query object
    random.shuffle(shuffled_products)
    return shuffled_products


def fetch_and_shuffle_products():
    """Fetch all products and shuffle them."""
    products = Product.query.all()  # Fetch all products
    random.shuffle(products)        # Shuffle the products
    return products


def fetch_all_category_products(category_key):
    """Fetch all uploaded products in the database for a given category.

    Args:
        category_key (str): The key representing the product category.

    Returns:
        list: A list of products belonging to the specified category.
    """
    return Product.query.filter_by(
        product_category=category_key
    ).order_by(Product.create_date.desc()).all()


def fetch_product_details(product_id, product_title):
    """Fetch product details based on product_id and product_title.

    Args:
        product_id (int): The unique identifier of the product.
        product_title (str): The title of the product.

    Returns:
        Product: The product details if found, otherwise None.
    """
    return Product.query.filter_by(
        item_id=product_id,
        product_title=product_title
    ).first()


def fetch_cart_records_by_user_bind_id(user_bind_id):
    """ This is a function that fetchs the user cart records
      stored in the shoppigcard table """
    return ShoppingCart.query.filter_by(
        user_bind_id=user_bind_id, product_status="not_paid").all()


def check_product_avaliablity(item_id):
    """ This is a function that return True or False if the product is
        available or not
    """

    product_details = Product.query.filter_by(item_id=item_id).first()
    return product_details


def check_product_already_exist_in_shoppingcart(item_id):
    """ This is a function that check if each item the user order is stored in
        the database
    """
    return True if ShoppingCart.query.filter_by(
        product_item_id=item_id).first() else False


def update_order_no(user_bind_id, item_id, new_order_no, product_qunatity):
    """ This function update the order no of each product in the
      shopping cart """

    try:
        uuid.UUID(user_bind_id)
    except ValueError:
        raise ValueError("user_bind_id must be a valid UUID")

    try:
        uuid.UUID(new_order_no)
    except ValueError:
        raise ValueError("new_order_no must be a valid UUID")

    # Check if the inputs are valid
    if not isinstance(item_id, int) or not isinstance(product_qunatity, int):
        raise ValueError(
            "item_id must be integers or product quantity must be an integer")

    # Query the shopping cart item
    shopping_item_details = ShoppingCart.query.filter_by(
        product_item_id=item_id, user_bind_id=user_bind_id).first()

    # Check if the item exists
    if shopping_item_details is None:
        raise ValueError("Item not found in the shopping cart")

    shopping_item_details.order_no = new_order_no
    shopping_item_details.product_qunatity = product_qunatity

    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError("Failed to update the shopping cart item") from e


def add_item_to_database(user_bind_id, item_details):
    """ This is a function that add the item to database """
    new_order_no = generate_order_no()
    for item in item_details:

        # Extract the quantity from the product_qunatity dictionary
        product_quantity = item['product_qunatity'].get('quantity', 0) if isinstance(item['product_qunatity'], dict) else item['product_qunatity']

        # Check if each product is stored in the database
        item_exits_in_database = check_product_already_exist_in_shoppingcart(
            item['item_id'])

        if item_exits_in_database:
            # Change the order number to a new order No
            update_order_no(
                user_bind_id,
                item['item_id'],
                new_order_no,
                product_quantity)
        else:
            # Add the product item to the shopping cart table
            store_new_item = ShoppingCart(
                    order_no=new_order_no,
                    product_item_id=item['item_id'],
                    user_bind_id=user_bind_id,
                    product_qunatity=product_quantity)
            db.session.add(store_new_item)
            db.session.commit()


def delete_cart_item(get_bindId, item_id):
    """ This is a function that delete the item once
      the user is authenicated """
    shopping_details = ShoppingCart.query.filter_by(
        product_item_id=item_id, user_bind_id=get_bindId).first()

    db.session.delete(shopping_details)
    db.session.commit()


def send_client_order(bind_id):
    """ This is a function the mail the client regarding their order """

    # Fetch all the item the client order
    shopping_records = fetch_cart_records_by_user_bind_id(bind_id)
    total_amt = 0

    if not shopping_records:
        return False

    user_data = get_user_by_bind_id(bind_id)

    if not user_data:
        return False

    order_key = get_order_key(bind_id)
    total_amt = get_total_amt(bind_id, order_key)  # noqa: F841

    subject = 'Approved Payment From Joam Collections'
    recipients = [user_data.email]
    body = 'TESTING MAIL'
    send_email(subject, recipients, body)
    return True
