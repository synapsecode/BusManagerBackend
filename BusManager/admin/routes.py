from flask import render_template, request, Blueprint, redirect, url_for, flash
from BusManager.models import DriverModel, AdminUser, StudentModel
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
@login_required
def admin_home():
	return render_template('admin_home.html')

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

@admin.route('/mark_payment_status', methods=['GET', 'POST'])
@login_required
def mark_payment_status():
	return render_template('markpaymentstatus.html', title='Mark Payment Status')

@admin.route('/get_journey_info', methods=['GET', 'POST'])
@login_required
def get_journey_info():
	return render_template('journey_info.html', title='Journey Information')

@admin.route('/verifydriver', methods=['GET', 'POST'])
@login_required
def verify_drivers():
	return render_template('verify_drivers.html', title='Verify Driver')


@admin.route('/verifystudent', methods=['GET', 'POST'])
@login_required
def verify_students():
	return render_template('verify_students.html', title='Verify Student')

@admin.route("/suspend_driver")
@login_required
def suspend_driver():
	drivers = DriverModel.query.all()
	return render_template('suspend_drivers.html', title='Suspend Drivers')

@admin.route("/suspend_student")
@login_required
def suspend_student():
	students = StudentModel.query.all()
	return render_template('suspend_students.html', title='Suspend Students')
	

"""
!Implementation Pending
Make something that can check each day how many days have passed
and automatically set is_paid of student to false if they have'nt paid.
if Payment Done, set last_paid_date
"""