"""
This is a module that define views routes for the users to access...
"""
from flask import (
    Blueprint,
    session,
    render_template,
    jsonify,
    request,
    redirect,
    url_for)
from website.clients.models.users import (
    get_user_by_bind_id,
    get_user_info_by_bind_id,
    send_client_order,
    delete_cart_item,
    check_product_avaliablity,
    add_item_to_database,
    fetch_cart_records_by_user_bind_id,
    fetch_all_products, fetch_eight_new_products,
    fetch_all_category_products,
    fetch_product_details,
    fetch_and_shuffle_products)
from website.clients.models.utils import (
    send_email_regarding_product_availablity)
from website.admin.models.admins import (
    get_product_by_item_id,
    get_order_key,
    get_total_amt)


# Define the BluePrint
views = Blueprint(
    "views", __name__,
    static_folder="website/clients/static",
    template_folder="website/clients/templates")


# Define the home route
@views.route("/")
def home():
    """This is a function that return the home page of our application"""

    # Check if the session is active
    session_status = False
    user_data = None
    table = "Home"

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    eight_newly_records = fetch_eight_new_products()
    shufled_product = fetch_and_shuffle_products()
    sliced_products = shufled_product[:10]

    return render_template(
        "home.html",
        eight_newly_records=eight_newly_records,
        session_status=session_status,
        user_data=user_data,
        shufled_product=sliced_products,
        table=table)


@views.route("/products")
def product_items():
    """ This is a function that render the product items page """

    # Check if the session is active
    session_status = False
    user_data = None
    title = "Trade With TayeOJ || Product"
    table = "Product"

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    products_data = fetch_all_products()

    return render_template(
        "item_category.html",
        title=title,
        table=table,
        products_data=products_data,
        session_status=session_status,
        user_data=user_data)

@views.route("/about-us")
def about_us():
    """ This is a function that render the about-us page"""

    # Check if the session is active
    session_status = False
    user_data = None
    title = "Trade With TayeOJ || Product"
    table = "About Us"

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    return render_template(
        "home.html",
        session_status=session_status,
        user_data=user_data,
        table=table)


@views.route('/contact-us')
def contact_us():
    """ This is a function that render the contact us"""

    # Check if the session is active
    session_status = False
    user_data = None
    title = "Trade With TayeOJ || Product"
    table = "Contact Us"

    return render_template(
        "home.html",
        session_status=session_status,
        user_data=user_data,
        table=table)


# Category views
@views.route("/product/<string:category>")
def product_category(category):
    """This function dynamically renders the products page for different categories."""

    # Default values
    session_status = False
    user_data = None
    title = "Trade With TayeOJ"
    category_table = {
        'vehicles': "Vehicles",
        'fashion-and-lifestyle': "Fashion & Lifestyle",
        "teddy_bears": "Teddy Bears",
        "food-beverages": "Food & Beverages",
        "electronics-technology": "Electronics & Technology",
        "indurial-suuplies": "Office Industrial Supplies",
        "agriculture&agro_allied": "Agriculture & Agro-Allied Services",
        "constructed-real_estate": "Construction & Real Estate",
        "energy_solution": "Energy Solutions",
        "oil-gas": "Oil & Gas",
        "fruits-veges": "Fruits & Veges"
    }

    # Check if the session is active
    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    # Map category to the appropriate table name and title
    table = category_table.get(category, "Unknown Category")
    if table == "Unknown Category":
        return "Category not found", 404  # Handle invalid categories

    # Adjust the page title based on the category
    title += f" || {table}"

    # Replace dashes with ampersands for fetching data if needed
    category_key = category.replace("-", "&")

    # Fetch products data
    products_data = fetch_all_category_products(category_key)

    return render_template(
        "item_category.html",
        title=title,
        table=table,
        products_data=products_data,
        session_status=session_status,
        user_data=user_data
    )


@views.route("/newly-arrived")
def new_arrived():
    """ This is a function that render the newly arrived products page """

    # Check if the session is active
    session_status = False
    user_data = None
    title = "Trade With TrayeOJ || Newly Arrived"
    table = "Newly Arrived"

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    products_data = fetch_all_products()

    return render_template(
        "item_category.html",
        title=title,
        session_status=session_status,
        products_data=products_data,
        table=table,
        user_data=user_data)


@views.route('/product-details/<int:product_id>/<string:product_title>')
def product_details(product_id, product_title):
    """ This is a function that render the product details """

    # Check if the session is active
    session_status = False
    user_data = None
    title = f"Trade With TrayeOJ || {product_title}"
    product_details = None
    table = "item details"

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

    product_details = fetch_product_details(product_id, product_title)
    shufled_product = fetch_and_shuffle_products()
    sliced_products = shufled_product[:10]

    return render_template(
        "item_category.html",
        title=title,
        table=table,
        session_status=session_status,
        shufled_product=sliced_products,
        product_details=product_details,
        user_data=user_data)

    


# cart Page
@views.route("/cart")
def cart_page():
    """ This is a function that return the cart page """

    # Check if the session is active
    session_status = False
    user_data = None
    title = "Joam Collections || Cart"
    total_amt = 0

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)

        order_key = get_order_key(get_bindId)
        total_amt = get_total_amt(get_bindId, order_key)

    return render_template(
        "cart.html", title=title,
        total_amt=total_amt,
        session_status=session_status,
        user_data=user_data)


@views.route('/checkout')
def checkout_page():
    """_summary_

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """
    session_status = False
    user_data = None
    title = "Joam Collections || Cart"
    total_amt = 0

    if 'bind_id' in session:
        session_status = True
        get_bindId = session.get('bind_id')
        user_data = get_user_by_bind_id(get_bindId)
        user_info_data = get_user_info_by_bind_id(get_bindId)

        order_key = get_order_key(get_bindId)
        total_amt = get_total_amt(get_bindId, order_key)
        formStatus = None

        if user_info_data:
            formStatus = "Develivered Form"

        return render_template(
            "checkout.html", title=title,
            total_amt=total_amt,
            session_status=session_status,
            formStatus=formStatus,
            user_data=user_data)
    else:
        return redirect(url_for('auth.clientLogin'))



############ HELPER ROUTES #############
@views.route("/fetch_cart_details", methods=["POST"])
def fetch_cart_details():
    """ This is a function the all the cart added throught the shoppigcart
        table or the clinet request
    """

    item_ids = request.json  # Receive item IDs sent from the client
    item_details = []
    stored_cart_items = []
    request_cart_items = []
    product_status = None
    get_bindId = None

    if 'bind_id' in session:
        stored_cart = None
        item_exits_in_database = None  # noqa: F841

        # Get the user bind id
        get_bindId = session.get('bind_id')

        # Check if the user an exist in the shooping cart
        stored_cart = fetch_cart_records_by_user_bind_id(get_bindId)

        if stored_cart:
            # Check if each product is available
            for cart_item in stored_cart:
                # Call the function to checkif the product is available
                product_info = check_product_avaliablity(
                    cart_item.product_item_id
                    )

                if product_info.market_status == "Available":

                    # add the product to the item details
                    stored_cart_items.append({
                        'item_id': cart_item.product_item_id,
                        'product_title': product_info.product_title,
                        'product_image': product_info.product_image,
                        'product_price': product_info.product_price,
                        'product_qunatity': cart_item.product_qunatity
                    })
                else:
                    # remove the item from shopping_cart table

                    # send an email regarding to that product status
                    send_email_regarding_product_availablity(
                        cart_item.item_id,
                        get_bindId)

    # else we read the item based on the client request

    for item_id, qunatity in item_ids.items():
        # Get the details of the product throught item id
        product_det = get_product_by_item_id(item_id)

        if product_det:
            # Check if the product is available
            product_status = check_product_avaliablity(product_det.item_id)

            if product_status:

                request_cart_items.append({
                    'item_id': product_det.item_id,
                    'product_title': product_det.product_title,
                    'product_image': product_det.product_image,
                    'product_price': product_det.product_price,
                    'product_qunatity': qunatity
                })
            else:
                # remove the from the localstorage
                pass

    # Compare stored_cart_items and request_cart_items arrays
    for cart_item in stored_cart_items:
        # If item_id is not present in request_cart_items,
        # add it to item_details
        if (
            cart_item['item_id']
            not in [item['item_id'] for item in request_cart_items]
        ):
            item_details.append(cart_item)

    # Add all items from request_cart_items to item_details
    item_details.extend(request_cart_items)

    # Pass the function to vailable and each product to the database
    if get_bindId is not None:
        print
        add_item_to_database(get_bindId, item_details)

    return jsonify(item_details)


@views.route("/delete_item", methods=["POST"])
def delete_item():
    """ This is a function that remove an item for the shoppingcart table """
    item_id = request.form.get('item_id')
    print('item_id', item_id)

    if 'bind_id' in session:
        # Get the user bind id
        get_bindId = session.get('bind_id')

        # Call a function that delee the product from the cart
        delete_cart_item(get_bindId, item_id)

    return jsonify({'message': 'Item deleted successfully'})


@views.route("/paid-items", methods=["POST"])
def paid_items():
    """ This is a function that send the admin and the client that the payment
    has been sent """
    sent_status = None

    if 'bind_id' in session:
        # Get the user bind id
        get_bindId = session.get('bind_id')

        # Send the client their order
        sent_status = send_client_order(get_bindId)

        if sent_status:
            return jsonify({'message': 'Success'})
        else:
            raise RuntimeError("Failed to send to client")
            return jsonify({'message': 'Failed to send to client'})
    else:
        raise RuntimeError("Failed to get the client ID")
        return jsonify({'message': 'Failed to get client'})


# User Account
@views.route("/account/profile")
def my_account():
    """ This is a function that render the client account """
    pass


@views.route("/account/notifications")
def notifications():
    """ This is a function that render the notification page """
    pass


@views.route("/account/track-item")
def track_item():
    """ This is a function that render the track item page """
    pass
