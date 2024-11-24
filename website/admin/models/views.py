"""
This is a module that define views routes for the users to access...
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from website.admin.models.admins import get_admin_by_bind_id, get_transcation_records, get_transcation_date, get_client_name, check_record_inserted_transcation, insert_new_record_transcation, update_shoppingcart_paymentstatus, update_transcation_records, get_order_by_order_id, get_item_title, get_item_img, get_item_amt, get_client_info, get_order_key, shoppingcart_status, fetch_transcation_records, get_order_status, get_order_date, get_total_amt, check_session, get_all_client_records, get_product_by_item_id, get_feedback_by_product_id, fetch_all_inboxs
from website.clients.models.users import get_user_by_bind_id, fetch_all_products
from website.clients.models.models import User, Feedback, ShoppingCart, TransactionHistory
from website import db
from website.admin.models.models import Product
from website.admin.models.utilities import allowed_file, random_string, get_day_suffix
import os
from werkzeug.utils import secure_filename
from operator import itemgetter


# Define the BluePrint
adminViews = Blueprint("adminViews", __name__, static_folder="website/admin/static", template_folder="website/admin/templates")

# Define the home route
@adminViews.route("/home")
def adminHome():
    """This is a function that return the home page of our application"""

    # Check session status and bind_id
    session_status, bind_id = check_session()

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    order_data = []
    shopping_cart_status = None

    # Fetch all the clients records
    client_data = get_all_client_records()

    # Fetch if there is a pending shopping cart
    shopping_cart_status = shoppingcart_status()

    if shopping_cart_status:
        for client in client_data:
            payment_date = get_order_date(client.bind_id)
            if payment_date is not None:
                order_data.append({
                    'order_no': get_order_key(client.bind_id),
                    'clientName': client.name,
                    'totalAmt': get_total_amt(client.bind_id, get_order_key(client.bind_id)),
                    'modePayment': "Online Transfer",
                    'paymentDate': get_order_date(client.bind_id),
                    'paymentState': get_order_status(client.bind_id, get_order_key(client.bind_id))
                })

    # Sort order_data based on paymentDate in descending order
    order_data = sorted(order_data, key=itemgetter('paymentDate'), reverse=True)
    order_data = order_data[:5]

    return render_template("adminHome.html", order_data=order_data, user_data=user_data)


@adminViews.route("/clients")
def clientsPage():
    """ This is a function that route the admin to the clients page """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Clients"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)

    # Fetch the clients records
    client_records = get_all_client_records()

    return render_template("adminTableList.html",
                            table=table,
                            client_records=client_records,
                            user_data=user_data)


@adminViews.route("/client/<uuid>", methods=['GET', 'POST'])
def clientDetailPage(uuid):
    
    if request.method == 'POST':
        client_bind_id = request.form.get("client_bind_id")
        purpose = request.form.get("purpose")

        if purpose == "Delete":

            # Delete the client from the User table
            client = get_user_by_bind_id(client_bind_id)

            if client:

                # Delete all records related to this client
                feedback_records = Feedback.query.filter_by(user_bind_id=client_bind_id).all()

                # delete all the feedback related to this client
                for record in feedback_records:
                    db.session.delete(record)

                shoppingcart_records = ShoppingCart.query.filter_by(user_bind_id=client_bind_id).all()

                # delete all the shopping cart related to this client
                for record in shoppingcart_records:
                    db.session.delete(record)

                transcation_records = TransactionHistory.query.filter_by(user_bind_id=client_bind_id).all()

                # delete all the shopping cart related to this client
                for record in transcation_records:
                    db.session.delete(record)

                # delete the client
                db.session.delete(client)
                db.session.commit()

                flash("Client records deleted successfully", category="success")
                return redirect(url_for('adminViews.clientsPage'))
            else:
                flash("An error occured getting the client", category="error")
                # return redirect(url_for('/admin/page/client/' + client_bind_id))
        elif purpose == "Edit":
            name = request.form.get('clientName')
            email = request.form.get('clientEmail')
            phone_number = request.form.get('clientPhoneNumber')

            # Check if that cient exist
            client = get_user_by_bind_id(client_bind_id)

            if client:
                client.name = name
                client.email = email
                client.phone_number = phone_number

                db.session.commit()
                flash("Successfully updated the client record", category="success")
                # return redirect(url_for("adminViews.clientDetailPage", client_bind_id="ea7ed3ad-4acd-44fa-8fde-3642f0471a26"))
            else:
                flash("An error occured getting the client", category="error")
                # return redirect(url_for('adminViews.clientDetailPage', client_bind_id=client_bind_id))
        else:
            flash("An error occured", category="error")
            # return redirect(url_for('adminViews.clientDetailPage', client_bind_id=client_bind_id))

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Clients"
    error_status = False

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    client_data = get_user_by_bind_id(uuid)

    # check if the client is vaild then fetch the records
    if client_data is None:
        flash("Client record not found", category="error")
        return redirect(url_for('adminViews.clientsPage'))

    return render_template("adminInfoDetails.html",
                            table=table,
                            client_data=client_data,
                            user_data=user_data)


# Page to delete client records
@adminViews.route("/product")
def product_page():
    """ This is the admin product page """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Product"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    return render_template("adminHome.html", table=table, user_data=user_data)


@adminViews.route("/product/upload_product", methods=['GET', 'POST'])
def upload_product():
    """ This is a function that add product items to the database """

    if request.method == 'POST':

        productCategory = request.form.get('productCategry')
        productTitle = request.form.get('productTitle')
        productDesc = request.form.get('productDesc')
        productPrice = request.form.get('productPrice')

        error_status = False

        if productCategory == '':
            error_status = True
            flash("Please select the product category", category="error")
        elif productTitle == '':
            error_status = True
            flash("Please enter the product title", category="error")
        elif productDesc == '':
            error_status = True
            flash("Please enter the product description", category="error")
        elif productPrice == '':
            error_status = True
            flash("Please enter the product price", category="error")

        # Handle file upload
        if 'productImage' in request.files:
            productImage = request.files['productImage']

            if productImage.filename == '':
                error_status = True
                flash("No selected file", category="error")

            if productImage and allowed_file(productImage.filename):
                # Create the uploads folder if it does not exist
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Generate a random string for the filename
                random_filename = random_string(10)

                # Get the file extension
                filename, extension = os.path.splitext(productImage.filename)

                # Update the filename with the random string and extension
                filename = f"{random_filename}{extension}"

                # Save the file with the updated filename
                filepath = os.path.join(upload_folder, filename)
                productImage.save(filepath)
        else:
            error_status = True
            flash("Invalid file format", category="error")

        if not error_status:
            # Save the file path to the database
            new_product = Product(product_category=productCategory,
                                    product_title=productTitle,
                                    product_image=filename,
                                    product_des=productDesc,
                                    product_price=productPrice)
            db.session.add(new_product)
            db.session.commit()
            flash("Uploaded Successfully", category="success")
            return redirect(url_for("adminViews.product_page"))

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Product"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    return render_template("adminUpload.html", table=table, user_data=user_data)


@adminViews.route("/product/lists")
def product_list():
    """ This is a function that fetch all the uploaded products """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Product"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)

    # Fetch the clients records
    product_records = fetch_all_products()
    return render_template("adminTableList.html", product_records=product_records, table=table, user_data=user_data)


@adminViews.route("/product/<int:item_id>", methods=['GET', 'POST'])
def product_details(item_id):
    """ This is a function that redirect the admin to the product details page """

    if request.method == "POST":
        product_id = request.form.get('product_item_id')
        purpose = request.form.get('purpose')

        try:
            product_id = int(product_id)

            if purpose == "Delete":

                # Fetch Product details
                product = get_product_by_item_id(product_id)

                if product:

                    # Delete all records related to this product
                    feedback_records = Feedback.query.filter_by( product_item_id=product_id).all()

                    # delete all the feedback related to this products
                    for record in feedback_records:
                        db.session.delete(record)

                    # Get the Product related to the Shopping cart
                    shoppingcart_records = ShoppingCart.query.filter_by(product_item_id=product_id).all()

                    # delete all the shopping cart related to this product
                    for record in shoppingcart_records:
                        db.session.delete(record)

                    # delete the client
                    db.session.delete(product)
                    db.session.commit()

                    flash("Product deleted successfully", category="success")
                    return redirect(url_for('adminViews.product_list'))
                else:
                    flash("An error occured getting the product", category="error")
            elif purpose == "Edit":

                # Fetch Product details
                product = get_product_by_item_id(product_id)

                if product:

                    # Get all the data
                    productCategory = request.form.get('productCategry')
                    productTitle = request.form.get('productTitle')
                    productDesc = request.form.get('productDesc')
                    productPrice = request.form.get('productPrice')
                    marketStatus = request.form.get('marketStatus')
                    error_status = False

                    if productCategory == '':
                        error_status = True
                        flash("Please select the product category", category="error")
                    elif productTitle == '':
                        error_status = True
                        flash("Please enter the product title", category="error")
                    elif productDesc == '':
                        error_status = True
                        flash("Please enter the product description", category="error")
                    elif productPrice == '':
                        error_status = True
                        flash("Please enter the product price", category="error")
                    elif marketStatus == '':
                        marketStatus = "Sold"

                    # Check if thw admin is going to change the product image
                    productImage = request.files['product_img']

                    if productImage.filename != '':
                        if productImage and allowed_file(productImage.filename):
                            # Create the uploads folder if it does not exist
                            upload_folder = current_app.config['UPLOAD_FOLDER']

                            if not os.path.exists(upload_folder):
                                os.makedirs(upload_folder)

                            # Generate a random string for the filename
                            random_filename = random_string(10)

                            # Get the file extension
                            filename, extension = os.path.splitext(productImage.filename)

                            # Update the filename with the random string and extension
                            filename = f"{random_filename}{extension}"

                            # Save the file with the updated filename
                            filepath = os.path.join(upload_folder, filename)
                            productImage.save(filepath)
                        else:
                            error_status = True
                            flash("Invalid file format", category="error")

                        # Update the product records with the image path
                        product.product_category = productCategory
                        product.product_title = productTitle
                        product.product_image = filename
                        product.product_des = productDesc
                        product.product_price = productPrice
                        product.market_status = marketStatus
                    else:
                        # Update the product records without the image path
                        product.product_category = productCategory
                        product.product_title = productTitle
                        product.product_des = productDesc
                        product.product_price = productPrice
                        product.market_status = marketStatus

                else:
                    error_status = True
                    flash("An error occured fetching the product record", category="error")

                if not error_status:
                    db.session.commit()
                    flash("Successfully updated the client record", category="success")
        except (ValueError, TypeError):
            raise ValueError("Product ID must be an integer")

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Product"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)

    # Fetch Product details
    product_data = get_product_by_item_id(item_id)

    # check if the client is vaild then fetch the records
    if product_data is None:
        flash("Product record not found", category="error")
        return redirect(url_for('adminViews.clientsPage'))

    # check for feedback for this product
    feedback_data = get_feedback_by_product_id(item_id)

    return render_template("adminInfoDetails.html",
                            table=table,
                            product_data=product_data,
                            feedback_data=feedback_data,
                            user_data=user_data)


@adminViews.route("/inboxs")
def inbox_list():
    """ This is a function that return the list of inboxs """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Inbox"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)

    # Fetct all the inboxs
    inbox_records = fetch_all_inboxs()
    return render_template("adminTableList.html", inbox_records=inbox_records, table=table, user_data=user_data)


@adminViews.route("/inboxs/<int:ticket_no>")
def inbox_details(ticket_no):
    """ This is a function that render the inbox details """
    pass


@adminViews.route("/records/transcation")
def transcation_history():
    """ This is a function that lists all the transcation made in this page """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Transcation History"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    transaction_records = []

    # Fetch all the transcation made in desc order
    transactions = fetch_transcation_records()

    # Listing out every details of the transcation
    for transcation in transactions:
        transaction_records.append({
            'order_no': transcation.cart_order_no,
            'transcation_ref': transcation.payment_ref,
            'client_name': get_client_name(transcation.user_bind_id),
            'transcation_amt': get_total_amt(transcation.user_bind_id, transcation.cart_order_no),
            'transcation_status': transcation.payment_status,
            'transcation_date': transcation.create_date
        })

    return render_template(
            "adminTableList.html",
            transaction_records=transaction_records,
            table=table,
            user_data=user_data)


@adminViews.route("/records/transcation/<order_no>", methods=["GET", "POST"])
def transcation_details(order_no):
    """ This is a function that render the transcation details """

    if request.method == "POST":
        purpose = request.form.get('purpose')
        
        if purpose == "Delete":
            order_no = request.form.get('order_no')
            user_bindId = request.form.get('user_bindId')
            delete_status = None

            delete_status = get_transcation_records(order_no, user_bindId)

            if delete_status:
                flash("Transcation record delete successfully", category="success")
                return redirect(url_for('adminViews.transcation_history'))
    
     # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Transcation"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    ordered_items = []

    # Fetch Product details
    order_data = get_order_by_order_id(order_no)

    # check if the client is vaild then fetch the records
    if order_data is None:
        flash("Transcation record not found", category="error")
        return redirect(url_for('adminViews.transcation_history'))


    client_details = get_client_info(order_no)
    total_amt = get_total_amt(client_details.bind_id, order_no)
    order_status = get_order_status(client_details.bind_id, order_no)
    order_date = get_transcation_date(order_no)

    for order in order_data:
        ordered_items.append({
            'product_title': get_item_title(order.product_item_id),
            'product_image': get_item_img(order.product_item_id),
            'product_amount': get_item_amt(order.product_item_id),
            'product_quanity': order.product_qunatity
        })
    return render_template("adminInfoDetails.html",
                            table=table,
                            ordered_items=ordered_items,
                            client_details=client_details,
                            total_amt=total_amt,
                            order_status=order_status,
                            order_no=order_no,
                            order_date=order_date,
                            user_data=user_data)


@adminViews.route("/records/orders")
def order_page():
    """ This is a function that return the list of order """

    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Order Records"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    shopping_cart_status = None
    order_data = []

    # Fetch all the clients records
    client_data = get_all_client_records()

    # Fetch if there is a pending shopping cart
    shopping_cart_status = shoppingcart_status()

    if shopping_cart_status:
        for client in client_data:
            payment_date = get_order_date(client.bind_id)
            if payment_date is not None:
                order_data.append({
                    'order_no': get_order_key(client.bind_id),
                    'clientName': client.name,
                    'totalAmt': get_total_amt(client.bind_id, get_order_key(client.bind_id)),
                    'paymentDate': get_order_date(client.bind_id),
                    'paymentStatus': get_order_status(client.bind_id, get_order_key(client.bind_id))
                })

    # Sort order_data based on paymentDate in descending order
    order_data = sorted(order_data, key=itemgetter('paymentDate'), reverse=True)

    return render_template(
            "adminTableList.html",
            order_data=order_data,
            table=table,
            user_data=user_data)


@adminViews.route("/records/order/<order_no>", methods=["GET", "POST"])
def order_details(order_no):
    """ This is function that display the order details to the admin """

    if request.method == "POST":
        purpose = request.form.get('purpose')

        if purpose == "Edit":
            order_no = request.form.get('order_no')
            user_bindId = request.form.get('user_bindId')
            update_status = request.form.get('update_status')
            transcation_status = None

            if update_status == "success":

                # Check if the record has been inserted in transcattion table
                transcation_status = check_record_inserted_transcation(order_no)

                if not transcation_status:
                    # inset the record
                    insert_new_record_transcation(order_no, user_bindId, update_status)
                    # Update the shopping cart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, "paid")
                else:
                    # update the transcation record
                    update_transcation_records(order_no, user_bindId, update_status)
                    # update the shoppingcart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, "paid")
            elif update_status == "not_paid":

                # Check if the record has been inserted in transcattion table
                transcation_status = check_record_inserted_transcation(order_no)

                if not transcation_status:
                    # inset the record
                    insert_new_record_transcation(order_no, user_bindId, update_status)
                    # Update the shopping cart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, update_status)
                else:
                    # update the transcation record
                    update_transcation_records(order_no, user_bindId, update_status)
                    # update the shoppingcart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, update_status)
            elif update_status == "error":

                # Check if the record has been inserted in transcattion table
                transcation_status = check_record_inserted_transcation(order_no)

                if not transcation_status:
                    # inset the record
                    insert_new_record_transcation(order_no, user_bindId, update_status)
                    # Update the shopping cart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, "not_paid")
                else:
                    # update the transcation record
                    update_transcation_records(order_no, user_bindId, update_status)
                    # update the shoppingcart
                    update_shoppingcart_paymentstatus(order_no, user_bindId, "not_paid")
            flash("Status updated successfully", category="success")
        elif purpose == "Delete":
            order_no = request.form.get('order_no')
            user_bindId = request.form.get('user_bindId')
            delete_status = None

            delete_status = delete_records_shoppingcart(user_bindId, order_no)

            if delete_status:
                flash("Order delete successfully", category="success")
                return redirect(url_for('adminViews.order_page'))

    
    # Check session status and bind_id
    session_status, bind_id = check_session()
    table = "Order"

    if not session_status:
        # If session is not active, redirect to login
        flash("Session has expired", category="error")
        return redirect(url_for('adminAuth.adminLogin'))

    user_data = get_admin_by_bind_id(bind_id)
    ordered_items = []

    # Fetch Product details
    order_data = get_order_by_order_id(order_no)

    # check if the client is vaild then fetch the records
    if order_data is None:
        flash("Order record not found", category="error")
        return redirect(url_for('adminViews.order_page'))


    client_details = get_client_info(order_no)
    total_amt = get_total_amt(client_details.bind_id, order_no)
    order_status = get_order_status(client_details.bind_id, order_no)
    order_date = get_order_date(client_details.bind_id)
    for order in order_data:
        ordered_items.append({
            'product_title': get_item_title(order.product_item_id),
            'product_image': get_item_img(order.product_item_id),
            'product_amount': get_item_amt(order.product_item_id),
            'product_quanity': order.product_qunatity
        })
    return render_template("adminInfoDetails.html",
                            table=table,
                            ordered_items=ordered_items,
                            client_details=client_details,
                            total_amt=total_amt,
                            order_status=order_status,
                            order_no=order_no,
                            order_date=order_date,
                            user_data=user_data)
