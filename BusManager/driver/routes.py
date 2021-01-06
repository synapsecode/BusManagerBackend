from flask import render_template, request, Blueprint, jsonify
from BusManager.models import LocationModel, DriverModel, StudentModel, JourneyModel
from BusManager import db
from BusManager.main.utils import verify_otp, send_otp
driver = Blueprint('driver', __name__)

"""
The Driver app works like this:

• Accept the Agreement
• Collect driver information like buss number
•Show loading or Please wait message while the admin is verifying.
• home page with TextField.
• The driver will enter the Studnet ID and check if the student have paid or not.

If the student have paid the driver can allow the student to enter the bus.

When the driver allows the student, automatically sends the student ID to the Admin.
The Admin will see each bus how many students are in with their ID

> Student Can Give Rating Too
"""

@driver.route("/")
def driver_home():
	return "BusManager<DRIVER>"

@driver.route("/register", methods=['POST'])
def driver_register():
	data = request.get_json()
	# print(data)
	name = data['name']
	phone = int(data['phone_number'])
	bus_number = data['bus_number']
	location = data['location']
	license_number = data['license_number']
	experience = int(data['experience'])
	#If Location Exists get it.
	loc = LocationModel.query.filter_by(location_name=location).first()
	if(loc == None):
		loc = LocationModel(location_name=location)
		db.session.add(loc)
		db.session.commit()
	
	driver = DriverModel(
		name=name,
		phone=phone,
		bus_number=bus_number,
		license_number=license_number,
		experience=experience,
		loc=loc
	)
	db.session.add(driver)
	db.session.commit()

	return jsonify({
		'status': 200,
		'message': 'Created Driver Account',
	})
	
	return "This is the driver module of BusManager"

@driver.route("/login")
def login_driver():
	send_otp('+919611744348')
	return f"Sent OTP"

@driver.route("/verifyotp/<otp>")
def verify_driver_otp(otp):
	return "Correct" if verify_otp('+919611744348', otp) else "Incorrect"

@driver.route("/allow_student", methods=['POST'])
def allow_student():
	data = request.get_json()
	sid = data['student_id']
	license_number = data['license_number']
	student = StudentModel.query.filter_by(student_id=sid).first()
	driver = DriverModel.query.filter_by(license_number=license_number).first()
	if(not driver):
		return jsonify({'status':0, 'message':'Invalid License Number'})
	if(not student):
		return jsonify({'status':0, 'message':'Invalid Student Phone Number'})
	if(not student.is_paid):
		return jsonify({'status':0, 'message':'Student Has not Paid'})
	print(f"DriverLocation: {driver.location}    ---->   StudentLocation: {student.location}")
	if(not student.location == driver.location):
		return jsonify({'status':0, 'message': 'Locations do not match'})
	#!Add Student to Journey
	#Success
	journey = JourneyModel(driver=driver, student=student)
	db.session.add(journey)
	db.session.commit()
	return jsonify({'status':200, 'message':'OK'})



@driver.route("/add_rating", methods=['POST'])
def add_rating():
	data = request.get_json()
	license_number = data['license_number']
	phone = int(data['student_phone'])
	rating = int(data['rating'])
	driver = DriverModel.query.filter_by(license_number=license_number).first()
	student = StudentModel.query.filter_by(phone=phone).first()
	if(not driver):  return jsonify({'status':0, 'message':'Invalid License Number'})
	if(not student): return jsonify({'status':0, 'message':'Invalid Student Phone Number'})
	driver.add_rating(rating) #Adds the Rating & Averages it
	return jsonify({'status':200, 'message':'OK'})

@driver.route("/edit_profile", methods=['POST'])
def edit_profile():
	data = request.get_json()
	license_number = data['license_number'] #Identifier
	driver = DriverModel.query.filter_by(license_number=license_number).first()
	if(not driver):  return jsonify({'status':0, 'message':'Invalid License Number'})

	name = data['name'] if data['name'] else driver.name
	phone = data['phone_number'] if data['phone_number'] else driver.phone
	bus_number = data['bus_number'] if data['bus_number'] else driver.bus_number
	experience = data['experience'] if data['experience'] else driver.experience
	location = driver.location[0]
	location.drivers.remove(driver) #Remove Existing Location
	if(data['location']): 
		if(LocationModel.query.filter_by(location_name=data['location']).first()):
			location = LocationModel.query.filter_by(location_name=data['location']).first()
		else:
			loc = LocationModel(location_name=data['location'])
			db.session.add(loc)
			db.session.commit()
			location = loc
	
	#!Handle Profile Image Updates

	#If such sensitive information changes, Driver must be reverified
	if(data['phone_number'] != driver.phone or data['bus_number'] != driver.bus_number or data['license_number'] != driver.license_number):
		driver.is_verified = False

	driver.name = name
	driver.phone = phone
	driver.bus_number = bus_number
	driver.experience = experience
	driver.license_number = data['license_number']
	location.drivers.append(driver) #Add Driver to New Location
	db.session.commit()
	return jsonify({'status':200, 'message':'Updated Data'})
