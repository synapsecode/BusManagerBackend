from flask import render_template, request, Blueprint, redirect, url_for, flash, jsonify
from BusManager.models import DriverModel, AdminUser, StudentModel
from BusManager.admin.forms import AdminLoginForm
from flask_login import login_user, current_user, logout_user, login_required
from BusManager import bcrypt, db
import datetime

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
	if(request.method == 'POST'):
		data = request.form
		id =int(data['id'])
		student = StudentModel.query.filter_by(id=id).first()
		if(not student): return jsonify({'status':0, 'message':'Invalid ID'})
		student.is_paid = True
		student.utc_last_paid = datetime.datetime.utcnow()
		db.session.commit()
		return redirect(url_for('admin.mark_payment_status'))

	students = StudentModel.query.all()
	
	# Performing Bulk Operation to Cancell Subscription of People Who are OverDue (30+Days)
	#This is redundant as we already check it everytime the service is used from Flutter
	for s in students:
		if((datetime.datetime.utcnow - s.utc_last_paid).days > 30):
			s.is_paid = False
			print(f"{s} is OverDue. Cancelling Subscription")
			db.session.commit()

	students = [s for s in students if not s.is_paid]

	return render_template('markpaymentstatus.html', title='Mark Payment Status', students=students)

@admin.route('/get_journey_info', methods=['GET', 'POST'])
@login_required
def get_journey_info():
	data = []
	drivers = DriverModel.query.all()
	for driver in drivers:
		jn = 0
		for journey in driver.journeys:
			if(journey.timestamp.day == datetime.datetime.utcnow().day):
				jn += 1
		data.append({'driver': driver, 'students': jn})
	return render_template('journey_info.html', title='Journey Information', data=data)


@admin.route('/verifydriver', methods=['GET', 'POST'])
@login_required
def verify_drivers():
	if(request.method == 'POST'):
		return redirect(url_for('admin.verify_drivers'))
	drivers = [d for d in DriverModel.query.all() if not d.is_verified]
	return render_template('verify_drivers.html', title='Verify Driver')


# @admin.route('/verifystudent', methods=['GET', 'POST'])
# @login_required
# def verify_students():
# 	if(request.method == 'POST'):
# 		return redirect(url_for('admin.verify_students'))
# 	students = [s for s in StudentModel.query.all() if not s.is_verified]
# 	return render_template('verify_students.html', title='Verify Student')

@admin.route("/suspend_driver", methods=['GET', 'POST'])
@login_required
def suspend_driver():
	if(request.method == 'POST'):
		data = request.form
		id = int(data['id'])
		driver = DriverModel.query.filter_by(id=id).first()
		if(not driver): return jsonify({'status':0, 'message':'Invalid ID'})
		print(f"Suspending {driver}")
		return redirect(url_for('admin.suspend_driver'))
	drivers = DriverModel.query.all()
	return render_template('suspend_drivers.html', title='Suspend Drivers', drivers=drivers)

@admin.route("/suspend_student", methods=['GET', 'POST'])
@login_required
def suspend_student():
	if(request.method == 'POST'):
		data = request.form
		id = int(data['id'])
		student = StudentModel.query.filter_by(id=id).first()
		if(not student): return jsonify({'status':0, 'message':'Invalid ID'})
		print(f"Suspending {student}")
		return redirect(url_for('admin.suspend_student'))
	students = StudentModel.query.all()
	return render_template('suspend_students.html', title='Suspend Students', students=students)
	

"""
!Implementation Pending
Make something that can check each day how many days have passed
and automatically set is_paid of student to false if they have'nt paid.
if Payment Done, set last_paid_date
"""