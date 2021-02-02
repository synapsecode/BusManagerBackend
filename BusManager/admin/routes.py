from flask import render_template, request, Blueprint, redirect, url_for, flash, jsonify
from BusManager.models import *
from BusManager.admin.forms import AdminLoginForm
from flask_login import login_user, current_user, logout_user, login_required
from BusManager import bcrypt, db
import datetime
from BusManager.student.routes import generate_student_id
import time
from BusManager.main.utils import AutomatedNotificationSender, delete_old_notificiations

admin = Blueprint('admin', __name__)

@admin.route("/")
@login_required
def admin_home():
	#Get all the Lapsed (expired Students) :: AutoRefind
	lapsed_students = len([s for s in StudentModel.query.all() if s.is_lapsed])
	#Get all the unpaid students :: NotAutoRefind
	unpaid_students = len([s for s in StudentModel.query.all() if not s.is_paid and not s.is_lapsed])
	#Get all the Unverified Drivers :: NotAutoFind
	unverified_drivers = len([d for d in DriverModel.query.all() if not d.is_verified])

	#!New Addition, Beware
	#Removes all the notifications that are beyond 1 day old
	delete_old_notificiations()

	return render_template(
		'admin_home.html',
	 	unverified_drivers=unverified_drivers, 
	 	unpaid_students=unpaid_students, 
	 	lapsed_students=lapsed_students
	)

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
		print(f"Marking Paid : {student}")
		student.is_paid = True #Marking Paid
		#Changing last paid to current date after payment (Used to mark 30days)
		student.utc_last_paid = datetime.datetime.utcnow()
		db.session.commit()
		return redirect(url_for('admin.mark_payment_status'))

	students = StudentModel.query.all()
	
	# Performing Bulk Operation to Cancell Subscription of People Who are OverDue (30+Days)
	#This is redundant as we already check it everytime the service is used from Flutter
	for s in students:
		if(s.utc_last_paid and (datetime.datetime.utcnow() - s.utc_last_paid).days > 30):
			s.is_paid = False
			print(f"{s} is OverDue. Cancelling Subscription")
			db.session.commit()

	#Get all the students who havent paid and arent expired
	students = [s for s in students if not s.is_paid and not s.is_lapsed]

	return render_template('markpaymentstatus.html', title='Mark Payment Status', students=students)

@admin.route('/get_journey_info')
@login_required
def get_journey_info():
	data = []
	drivers = DriverModel.query.all()
	#get the Number of journeys per driver for TODAY's day
	for driver in drivers:
		jn = 0
		for journey in driver.journeys:
			if(journey.timestamp.day == datetime.datetime.utcnow().day):
				jn += 1
		data.append({'driver': driver, 'students': jn})
	return render_template('journey_info.html', title='Journey Information', data=data)

@admin.route('/get_journey_details/<driver_id>')
@login_required
def get_journey_details(driver_id):
	driver = DriverModel.query.filter_by(id=driver_id).first()
	if(not driver): return jsonify({'status':0, 'message':'No Driver Found'})
	students = []
	#Get all the Students for the Driver's Individual Journeys
	for journey in driver.journeys:
		if(journey.timestamp.day == datetime.datetime.utcnow().day):
			students.append(journey.student)
	return render_template('journey_details.html', title='Journey Details', students=students, driver=driver)


@admin.route('/verifydriver', methods=['GET', 'POST'])
@login_required
def verify_drivers():
	if(request.method == 'POST'):
		data = request.form
		driver = DriverModel.query.filter_by(id=int(data['id'])).first()
		if(not driver): return jsonify({'status':0, 'message':'No Driver with that ID'})
		driver.is_verified = True #Verifying Drivers
		db.session.commit()
		print(f"Successfully Verified {driver}")
		return redirect(url_for('admin.verify_drivers'))
	drivers = [d for d in DriverModel.query.all() if not d.is_verified]
	return render_template('verify_drivers.html', title='Verify Driver', drivers=drivers)


@admin.route('/reallocateid', methods=['GET', 'POST'])
@login_required
def reallocate_student_id():
	if(request.method == 'POST'):
		data = request.form
		id = int(data['id'])
		student = StudentModel.query.filter_by(id=id).first()
		lapsed_instance = LapsedStudents.query.filter_by(sid=id).first()
		if(not student): return jsonify({'status':0, 'message':'Invalid Student ID'})
		if(not lapsed_instance): return jsonify({'status': 0, 'message': 'Student ID has not lapsed 6 months'})
		print(f"Reallocating StudentID & Marking Paid for {student}")
		student.created_on = datetime.datetime.utcnow() #Change CreatedOn to Today
		student.is_paid = True #Set IsPaid to True
		student.utc_last_paid = datetime.datetime.utcnow() #Set last Paid to Today
		student.student_id = generate_student_id(6) #Generate a new Student ID
		db.session.delete(lapsed_instance) #Remove LapsedStudent Instance
		db.session.commit()
		return redirect(url_for('admin.reallocate_student_id'))
	lapsed_students = [l.get_student for l in LapsedStudents.query.all()]
	return render_template('reallocate.html', title='Reallocate Student ID', lapsed_students=lapsed_students)

@admin.route("/delete_drivers", methods=['GET', 'POST'])
@login_required
def delete_drivers():
	if(request.method == 'POST'):
		data = request.form
		id = int(data['id'])
		driver = DriverModel.query.filter_by(id=id).first()
		if(not driver): return jsonify({'status':0, 'message':'Invalid ID'})
		print(f"Deleteing {driver}")
		db.session.delete(driver)
		db.session.commit()
		return redirect(url_for('admin.delete_drivers'))
	drivers = DriverModel.query.all()
	return render_template('delete_drivers.html', title='Delete Drivers', drivers=drivers)

@admin.route("/managestudents", methods=['GET', 'POST'])
@login_required
def delete_students():
	if(request.method == 'POST'):
		data = request.form
		id = int(data['id'])
		student = StudentModel.query.filter_by(id=id).first()
		if(not student): return jsonify({'status':0, 'message':'Invalid ID'})
		print(f"Deleteing {student}")
		db.session.delete(student)
		db.session.commit()
		return redirect(url_for('admin.delete_students'))
	students = StudentModel.query.all()
	return render_template('delete_students.html', title='Delete Students', students=students)

#-------------------------------------------DATA---------------------------------------------
@admin.route('/viewdata/locations')
@login_required
def data_locations():
	locations = LocationModel.query.all()
	data = []
	for L in locations:
		data.append({
			'location_name': L.location_name,
			'id': L.id,
			'members': len(L.students.all()) #+ len(L.drivers.all()),
		})
	return render_template('getdata/locations.html', locations=data, title='Locations')

@admin.route('/viewdata/timings/<tid>')
@login_required
def data_timings(tid):
	location = LocationModel.query.filter_by(id=tid).first()
	if(not location): return jsonify({'status':0, 'message':'No Such Location'})
	data = []
	all_timings = TimingModel.query.all()
	for T in all_timings:
		members = 0

		#Get all students of current location
		students = [x for x in T.students.all() if x.location[0] == location]

		
		members += len(students)

		data.append({
			'id': T.id,
			'start': T.start,
			'end': T.end,
			'members': members,
		})
	
	return render_template('getdata/timings.html', timings=data, title='timings', location=location.location_name, tid=tid)

@admin.route('/viewdata/grouped_data/<lid>/<tid>')
@login_required
def data_allgrouped(lid, tid):
	T = TimingModel.query.filter_by(id=tid).first()
	if(not T): return jsonify({'status':0, 'message':'Invalid Timing ID'})
	L = LocationModel.query.filter_by(id=lid).first()
	if(not L): return jsonify({'status':0, 'message':'Invalid Location ID'})

	#Get all student from Current Timing who have the same location
	students = [x for x in T.students.all() if x.location[0] == L]


	return render_template('getdata/groupeddata.html', timings=T, students=students, location=L.location_name)


@admin.route('/studentprofile/<sid>')
@login_required
def student_profile(sid):
	student = StudentModel.query.filter_by(id=sid).first()
	if(not student): return jsonify({'status':0, 'message':'No Student'})
	return render_template('getdata/profileimg.html', title='Student Profile', student=student)
#--------------------------------------------------------------------------------------------

@admin.route('/driverprofile/<did>')
@login_required
def driver_profile(did):
	driver = DriverModel.query.filter_by(id=did).first()
	timings = [f"{T.start} to {T.end},\t" for T in driver.timings]
	if(not driver): return jsonify({'status':0, 'message':'No Driver'})
	return render_template('getdata/driverprofile.html', title='Driver Profile', driver=driver, timings=timings)

@admin.route('/notifystudents')
@login_required
def notify_students():
	T = time.localtime()
	dt = datetime.datetime.utcnow()
	timestamp = f"{dt.day}/{dt.month}/{dt.year} {T.tm_hour}:{T.tm_min}"
	message = "Pickup time Has Started!"
	sender = "Admin"

	#Removes all the notifications that are beyond 1 day old
	delete_old_notificiations()

	notification = NotificationModel(
		sender=sender, 
		message=message, 
		timestamp=timestamp
	)
	db.session.add(notification)
	db.session.commit()
	
	#Keeps sending the Messages repeatedly in 20 minute intervals, 4 times
	AutomatedNotificationSender()
	return redirect(url_for('admin.admin_home'))



@admin.route('/add_data')
@login_required
def add_data():
	locations = LocationModel.query.all()
	universities = UniversityModel.query.all()
	admin = AdminUser.query.all()[0]
	return render_template('add_data.html', title='Add Data', locations=locations, universities=universities, admin=admin)


@admin.route('/add_data_actions/<action>/<id>', methods=['GET', 'POST'])
@login_required
def add_data_actions(action, id):
	if(request.method == 'POST'):
		data = request.form
		if(action == 'LOCADD'):
			loc = LocationModel(location_name=data['location_name'].lower())
			db.session.add(loc)
			db.session.commit()
		if(action == 'UNIADD'):
			uni = UniversityModel(name=data['uni_name'].lower(), address=data['uni_addr'].lower())
			db.session.add(uni)
			db.session.commit()
		if(action == 'TEXTADD'):
			admin = AdminUser.query.all()[0]
			pending_text = data['pending_text']
			expired_text = data['expired_text']
			admin.pendingtext = pending_text
			admin.expiredtext = expired_text
			db.session.commit()
		return redirect(url_for('admin.add_data'))

	if(action == 'LOCDEL'):
		loc = LocationModel.query.filter_by(id=id).first()
		if(not loc): return "NO SUCH LOCATION"
		loc.students = []
		loc.drivers = []
		db.session.delete(loc)
		db.session.commit()
	elif(action == 'UNIDEL'):
		uni = UniversityModel.query.filter_by(id=id).first()
		if(not uni): return "NO SUCH UNIVERSITY"
		db.session.delete(uni)
		db.session.commit()
	return redirect(url_for('admin.add_data'))