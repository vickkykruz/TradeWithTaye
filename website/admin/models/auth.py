"""
This is a module that define and handle the authenication of the the
adminstrators
"""


from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from website import db
from website.clients.models.password_utils import set_password, check_password
from website.clients.models.users import validate_email
from website.admin.models.admins import get_admin_by_email

# Define the BluePrint
adminAuth = Blueprint("adminAuth", __name__, static_folder="website/clients/static", template_folder="website/admin/templates")


@adminAuth.route("/logout")
def clientLogout():
    """ This is a function that logout the user from their account """
    session.pop('adminBind_id', None)
    flash(" You are logged out successfully ", category="success")
    return redirect(url_for('adminAuth.adminLogin'))


@adminAuth.route('/login', methods=['GET', 'POST'])
def adminLogin():
    """ This is a function that authenicate the admin then redirect them to
        the index page
    """
    if request.method == 'POST':
        admin_email = request.form.get("email")
        admin_password = request.form.get("password")

        # Debugging output to check the received data
        status_field = None  # Default value for status_field
        error_status = False
        fetch_user_details = None
        vaildate_data = None

        # Vaildae the input field
        if not admin_email:
            error_status = True
            flash("Please enter your email address", category="error")
        elif not admin_password:
            error_status = True
            flash("Please enter your password", category="error")
        else:
            # Checking if the user exists
            if validate_email(admin_email):
                validate_data = get_admin_by_email(admin_email)
            else:
                error_status = True
                flash("Invaild email address", category="error")

            # Display error indicating the user don't exists
            if validate_data is None:
                error_status = True
                flash("This account does not exists", category="error")

        if not error_status:
            # Get the user's hash_password
            hash_password = validate_data.password_hash

            # Check if the password matches
            if check_password(hash_password, admin_password):
                # Fetch the user bind_id and use it as the session key for that user
                fetch_user_details = validate_data
                session['adminBind_id'] = fetch_user_details.bind_id
                session.permanent = True
                flash(" You are welcome ", category="success")
                # Redirect the user to either the home page or the cart page
                return redirect(url_for('adminViews.adminHome'))
            else:
                flash("Incorrect password", category="error")

    return render_template("adminLogin.html")
