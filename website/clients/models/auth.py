"""
This is a module that define auth routes for the users to access...
"""
# import pdb # For debugging
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash)
from website.clients.models.models import User
# from website.admin.models.models import Admin
# from website.admin.models.admins import get_admin_by_email
from website.clients.models.password_utils import set_password, check_password
from website import db
from website.clients.models.users import (
    validate_email,
    validate_phone_number,
    get_user_by_email,
    get_user_by_phone_number)

# Define the BluePrint
auth = Blueprint("auth", __name__,
                 static_folder="website/clients/static",
                 template_folder="website/clients/templates")


# Define the routes for user authenication
@auth.route("/login", methods=['GET', 'POST'])
def clientLogin():
    """ This is a function that login the user to their account """
    if request.method == 'POST':
        user_info = request.form.get('user_info')
        user_password = request.form.get('user_password')
        # Get the 'cart' query parameter from the URL
        keyvalue1 = request.args.get('cart')

        status_field = None  # Default value for status_field
        error_status = False
        fetch_user_details = None
        vaildate_data = None

        # Vaildae the input field
        if not user_info:
            error_status = True
            flash(
                "Please enter your email address or phone number",
                category="error")
        elif not user_password:
            error_status = True
            flash("Please enter your password", category="error")
        elif not (validate_email(user_info) or validate_phone_number(user_info)):
            error_status = True
            flash("Error: Unable to detect if it is a phone number or an email address. Please try again", category="error")
        else:
            # Checking if the user exists
            if validate_email(user_info):
                status_field = "email"
                validate_data = get_user_by_email(user_info)
            elif validate_phone_number(user_info):
                status_field = "phone"
                validate_data = get_user_by_phone_number(user_info)

             # Display error indicating the user don't exists
            if validate_data is None:
                error_status = True
                flash("This account does not exists", category="error")

        if not error_status:
            # Get the user's hash_password
            hash_password = validate_data.password_hash

            # Check if the password matches
            if check_password(hash_password, user_password):
                # Fetch the user bind_id and use it as the session key for that user
                fetch_user_details = validate_data
                session['bind_id'] = fetch_user_details.bind_id

                # Redirect the user to either the home page or the cart page
                if keyvalue1 == "Signup":
                    return redirect(url_for('views.checkout_page'))
                elif keyvalue1 == "Item":
                    keyValue2 = request.args.get('item_id')
                    keyValue3 = request.args.get('item_title')
                    return redirect(url_for('views.product_details', product_id=keyValue2, product_title=keyValue3))
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password", category="error")

    return render_template("login.html")

@auth.route("/logout")
def clientLogout():
    """ This is a function that logout the user from their account """
    session.pop('bind_id', None)
    return redirect(url_for('auth.clientLogin'))

@auth.route("/register", methods=['GET', 'POST'])
def clientRegister():
    """ This is a function that register the user to their account """
    if request.method == 'POST':
        # pdb.set_trace()
        user_name = request.form.get('user_name')
        user_info = request.form.get('user_info')
        user_password = request.form.get('user_password')
        confirm_password = request.form.get('confirm_password')

        status_field = None  # Default value for status_field
        error_status = False
        fetch_user_details = None
        vaildate_data = None
        hashed_password = None

        # Vaildae the input field
        if user_name == '':
            error_status = True
            flash("Please enter your name", category="error")
        elif user_info == '':
            error_status = True
            flash("Please enter your email address or phone number", category="error")
        elif user_password == '':
            error_status = True
            flash("Please enter your password", category="error")
        elif confirm_password == '':
            error_status = True
            flash("Please enter your confirm password", category="error")
        elif user_password != confirm_password:
            error_status = True
            flash("Password do not match", category="error") 
        elif not (validate_email(user_info) or validate_phone_number(user_info)):
            error_status = True
            flash("Error: Unable to detect if it is a phone number or an email address. Please try again", category="error")
        else:
            # Checking if the user exists
            if validate_email(user_info):
                status_field = "email"
                validate_data = get_user_by_email(user_info)
            elif validate_phone_number(user_info):
                status_field = "phone"
                validate_data = get_user_by_phone_number(user_info)

            # Display error indicating the user exists
            if validate_data is not None:
                error_status = True
                flash("This account already exists", category="error")

             # Generate a password_hash for the password
            hashed_password = set_password(user_password)

            if hashed_password is None:
                error_status = True
                flash("Internal Error: Unable to create an account", category="error")



        if not error_status and status_field:
            # Define the user
            if status_field == "email":
                new_user = User(name=user_name, email=user_info, password_hash=hashed_password)
            else:
                new_user = User(name=user_name, phone_number=user_info, password_hash=hashed_password)
            # new_user.set_password(user_password)

            # Add the user to the database
            db.session.add(new_user)
            # Tell the database we have made changes
            db.session.commit()

            # Fetch the user bind_id and use it as the session key for that user
            fetch_user_details = validate_data or new_user
            session['bind_id'] = fetch_user_details.bind_id

            # Redirect the user to either the home page or the cart page
            return redirect(url_for('views.home'))

    return render_template("register.html")

@auth.route("/forgotting-password")
def clientForgotPassword():
    """ This is a function that logout the user from their account """
    return render_template("forgot-password.html")
