"""
This is a module that handle that the following
"""


import uuid
from flask_mail import Message
from website import mail


def generate_order_no():
    return str(uuid.uuid4())


def send_email_regarding_product_availablity():
    """ This is a function that send the user an mail regarding to the
        unavailablity of the product
    """
    pass


def send_email(subject, recipients, body):
    """ This is a function that handle the email to client / admin """

    msg = Message(subject, sender=('Sender Name','info@joamcollections.com.ng'), recipients=recipients)
    msg.body = body
    mail.send(msg)

