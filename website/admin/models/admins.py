""" This is a modue that deals with the functionality of the admin """

import random
import uuid
import re
from website import db
from flask import session
from website.admin.models.models import Admin, Product
from website.clients.models.models import User, Feedback, Inbox, ShoppingCart, TransactionHistory


# Fetching a user data thorogh their email address
def get_admin_by_email(email):
    """ This return the query data of the search admin """
    return Admin.query.filter_by(email=email).first()


# Fetching the user data through their session bind_id
def get_admin_by_bind_id(bind_id):
    """ This is a function that return the user data as a dictionary """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    return Admin.query.filter_by(bind_id=bind_id).first()


# Helper function to check session status and presence of bind_id
def check_session():
    """ This return the session status and the admin bind_id """
    session_status = False
    adminBind_id = None

    if 'adminBind_id' in session:
        session_status = True
        adminBind_id = session.get('adminBind_id')

    return session_status, adminBind_id


# Fetch all the user records
def get_all_client_records():
    """ This is a function that fetch all the clients registered on the application """
    return User.query.all()


def get_product_by_item_id(item_id):
    """ This is a function that fetch the product data """
    #print('item_id:', item_id, 'type:', type(item_id))
    item_id = int(item_id)

    if not isinstance(item_id, int):
        raise ValueError("item_i must be an integer")
    return Product.query.filter_by(item_id=item_id).first()


def get_feedback_by_product_id(item_id):
    """ This is a function that fetch all the feedback record related to the product """
    if not isinstance(item_id, int):
        raise ValueError("item_id must be an integer")
    return Feedback.query.filter_by(product_item_id=item_id).all()


def fetch_all_inboxs():
    """ This is a function that return all the uploaded inboxs in the
        database
    """
    return Inbox.query.order_by(Inbox.create_date.desc()).all()

def get_total_amt(bind_id, order_no):
    """ This is a function that get the total amount items the user ordered """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    total_amount = 0
    shopping_array = ShoppingCart.query.filter_by(user_bind_id=bind_id, order_no=order_no).all()

    for product in shopping_array:

        product_detail = Product.query.filter_by(item_id=product.product_item_id).first()
        product_amt = product_detail.product_price
        total_amount += product_amt * product.product_qunatity

    return total_amount


def get_order_date(bind_id):
    """ This is a function that get the first date the user order """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    shopping_details = ShoppingCart.query.filter_by(user_bind_id=bind_id, product_status="not_paid").first()
    
    if shopping_details is not None:
        return shopping_details.create_date
    else:
        return None


def get_order_key(bind_id):
    """ This is a function that return the first order key of the user desc """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    shopping_details = ShoppingCart.query.filter_by(
            user_bind_id=bind_id,
            product_status="not_paid"
            ).order_by(ShoppingCart.create_date.desc()).first()

    if shopping_details is not None:
        return shopping_details.order_no
    else:
        return None


def get_order_status(bind_id, order_no):
    """ This is a function that give the order status """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    transcation_detail = TransactionHistory.query.filter_by(user_bind_id=bind_id, cart_order_no=order_no).first()
    return transcation_detail.payment_status if transcation_detail else "not paid"


def fetch_transcation_records():
    """ This is a fuction that query out the transcation records to the admin """

    return TransactionHistory.query.order_by(TransactionHistory.create_date.desc()).all()


def get_client_name(bind_id):
    """ This is a function that return the client name """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    client_details = User.query.filter_by(bind_id=bind_id).first()
    return client_details.name


def shoppingcart_status():
    """ This is a function return true if there is records else false """

    shopping_details = ShoppingCart.query.filter_by(product_status="not_paid").all()
    return True if shopping_details else False


def get_item_title(item_id):
    """ This is function return the title of the product """

    if not isinstance(item_id, int):
        raise ValueError("item_id must be an integer")

    product_details = Product.query.filter_by(item_id=item_id).first()
    return product_details.product_title if product_details else None


def get_item_img(item_id):
    """ This function return the image url of the product """

    if not isinstance(item_id, int):
        raise ValueError("item_id must be an integer")

    product_details = Product.query.filter_by(item_id=item_id).first()
    return product_details.product_image if product_details else None


def get_item_amt(item_id):
    """ This is a function that return the amount of the product """

    if not isinstance(item_id, int):
        raise ValueError("item_id must be an integer")

    product_details = Product.query.filter_by(item_id=item_id).first()
    return product_details.product_price if product_details else None


def get_client_info(order_no):
    """ This is a function that fetch the user information beside on order_no desc first """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    order_details = ShoppingCart.query.filter_by(order_no=order_no).order_by(ShoppingCart.create_date.desc()).first()

    if order_details:
        client_data = User.query.filter_by(bind_id=order_details.user_bind_id).first()
        return client_data


def get_order_by_order_id(order_no):
    """ This is a function that return all the items the user selected """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    # selected_item = ShoppingCart.query.filter_by(order_no=order_no).all()
    selected_item = ShoppingCart.query.filter_by(order_no=order_no).all()
    if selected_item:
        return selected_item


def check_record_inserted_transcation(order_no):
    """ This function return True to records found else False"""

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    transaction_details = TransactionHistory.query.filter_by(cart_order_no=order_no).all()
    return True if transaction_details else False


def insert_new_record_transcation(order_no, user_bindId, update_status):
    """ This is a function that insert the records into transcation table """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    try:
        uuid.UUID(user_bindId)
    except ValueError:
        raise ValueError("user_bindId must be a vaild UUID")

    if not isinstance(update_status, str):
        raise ValueError("update_status must be a vaild string")

    add_transcation_record = TransactionHistory(
            user_bind_id=user_bindId,
            cart_order_no=order_no, payment_status=update_status)

    db.session.add(add_transcation_record)
    db.session.commit()


def update_shoppingcart_paymentstatus(order_no, user_bindId, update_status):
    """ This is a function that update the record from shoppingcart table """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    try:
        uuid.UUID(user_bindId)
    except ValueError:
        raise ValueError("user_bindId must be a vaild UUID")

    if not isinstance(update_status, str):
        raise ValueError("update_status must be a vaild string")

    cart_details = ShoppingCart.query.filter_by(order_no=order_no, user_bind_id=user_bindId).all()

    if cart_details is None:
        raise ValueError("Cart items not found")

    for cart in cart_details:
        cart.product_status = update_status

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError("Failed to update the shopping cart item") from e


def update_transcation_records(order_no, user_bindId, update_status):
    """ This is a function that update the transcation records """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    try:
        uuid.UUID(user_bindId)
    except ValueError:
        raise ValueError("user_bindId must be a vaild UUID")

    if not isinstance(update_status, str):
        raise ValueError("update_status must be a vaild string")

    transcation_details = TransactionHistory.query.filter_by(user_bind_id=user_bindId, cart_order_no=order_no).first()

    if transcation_details is None:
        raise ValueError("transcation_details not found")

    transcation_details.payment_status = update_status

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError("Failed to update the transcation record") from e


def get_transcation_date(order_no):
    """ This is a function that get transcation date """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_ must be a vaild uuid")

    transcate_date = TransactionHistory.query.filter_by(cart_order_no=order_no).first()
    return transcate_date.create_date if transcate_date else None


def get_transcation_records(order_no, user_bindId):
    """ This is a function that delete the cart and transcaion then return True """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    try:
        uuid.UUID(user_bindId)
    except ValueError:
        raise ValueError("user_bindId must be a vaild UUID")

    shoppingcart_status = None
    transcation_records = TransactionHistory.query.filter_by(user_bind_id=user_bindId, cart_order_no=order_no).first()

    if transcation_records is not None:
        shoppingcart_status = delete_records_shoppingcart(user_bindId, order_no)
        if shoppingcart_status:
            db.session.delete(transcation_records)
            db.session.commit()

            return True
        else:
            return False
    else:
        return False


def delete_records_shoppingcart(user_bindId, order_no):
    """ This is a function that delete the item in the shopping cart """

    try:
        uuid.UUID(order_no)
    except ValueError:
        raise ValueError("order_no must be a vaild UUID")

    try:
        uuid.UUID(user_bindId)
    except ValueError:
        raise ValueError("user_bindId must be a vaild UUID")

    shoppingcart_records = ShoppingCart.query.filter_by(order_no=order_no, user_bind_id=user_bindId).all()

    if shoppingcart_records:
        for cart in shoppingcart_records:
            db.session.delete(cart)

        db.session.commit()
        return True
    else:
        return False
