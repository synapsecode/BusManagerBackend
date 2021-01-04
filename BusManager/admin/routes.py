from flask import render_template, request, Blueprint, redirect, url_for, flash
from BusManager.models import DriverModel, AdminUser
from BusManager.admin.forms import AdminLoginForm
from flask_login import login_user, current_user, logout_user, login_required
from BusManager import bcrypt

admin = Blueprint('admin', __name__)

"""
The Admin section:

As an Admin wants to know:
• From which number the student sent the money.
• Checking the driver info.
• How many students are entered each bus with their IDs
Basically All the GLobal Information! > FlaskWTF
"""

@admin.route("/")
def admin_home():
	return "This is the admin module of BusManager"

@admin.route("/login", methods=['GET', 'POST'])
def adminlogin():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = AdminLoginForm()
	if(form.validate_on_submit()):
		admin = AdminUser.query.filter_by(username=form.username.data).first()
		if(admin and bcrypt.check_password_hash(admin.password, form.password.data)):
			login_user(admin, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('adminlogin.html', title='Admin Login', form=form)


@admin.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('admin.adminlogin'))


@admin.route("/suspend_driver")
def suspend_driver():
	drivers = DriverModel.query.all()
	


"""
!Implementation Pending
Make something that can check each day how many days have passed
and automatically set is_paid of student to false if they have'nt paid.
if Payment Done, set last_paid_date
"""