from flask import render_template, request, Blueprint, jsonify, session
from BusManager.models import *
from BusManager import db
from BusManager.main.utils import generate_session_id, send_otp, upload_file_to_cloud, verify_otp, verify_session_key
import random
import io
from BusManager.main.utils import printlog
driver = Blueprint('driver', __name__)


@driver.route("/")
def driver_home():
	return "BusManager<DRIVER> API :: MAIN"

@driver.route("/register", methods=['POST'])
def driver_register():
	data = request.get_json()
	# Get Data
	name = data['name']
	phone = data['phone_number']
	bus_number = data['bus_number']
	location = data['location']
	license_number = data['license_number']
	experience = int(data['experience'])
	timings = list(data['timings']) #[[8:00AM, 3:40PM], [9:30AM, 5:00PM]]

	#If Location Exists get it.
	loc = LocationModel.query.filter_by(location_name=location.lower()).first()
	if(loc == None):
		loc = LocationModel(location_name=location.lower())
		db.session.add(loc)
		db.session.commit()

	#---------------------------Timings----------------------

	TimingsList = []
	for TList in timings:
		S, E = rectify_timings(TList[0], TList[1])
		T = TimingModel.query.filter_by(start=S, end=E).first()
		if(not T):
			T = TimingModel(start=S, end=E)
			db.session.add(T)
			db.session.commit()
		TimingsList.append(T)

	#------------------------------------------------------
	
	driver = DriverModel(
		name=name,
		phone=phone,
		bus_number=bus_number,
		license_number=license_number,
		experience=experience,
		loc=loc,
		timings_list=TimingsList
	)
	db.session.add(driver)
	db.session.commit()

	#Send the OTP Immediately after Registration
	send_otp(phone)

	return jsonify({
		'status': 200,
		'message': 'Created Driver Account',
	})

@driver.route('/getdriver/<phone>')
def getdriver(phone):
	if(not verify_session_key(request, phone)): return jsonify({'status':0, 'message':'SessionFault'})
	driver = DriverModel.query.filter_by(phone=phone).first()
	if(not driver): return jsonify({'status':0, 'message':'No Driver with that Phone Number'})
	return jsonify({
		'status':200,
		'message':'OK',
		'driver': driver.get_json_representation()	
	})

@driver.route("/resend_otp/<phone>")
def resend_otp(phone):
	send_otp(phone)
	return jsonify({'status':200, 'message':'OK'})

@driver.route("/verifyphone/<phone>/<otp>")
def verify_driver_otp(phone, otp):
	is_correct = verify_otp(phone, otp)
	if(is_correct):
		driver = DriverModel.query.filter_by(phone=phone).first()
		if(not driver): return jsonify({'status':0, 'message':'No Driver with that Phone Number'})
		driver.phone_verified = True #Verify Driver
		db.session.commit()
		printlog(f"{driver} -> {driver.phone_verified}")
		#---------------------------------LOGINREDIRECT----------------------------------------
		S = SessionModel.query.filter_by(phone=driver.phone).first()
		if(not S):
			sessionkey = generate_session_id() #Generate Session ID
			S = SessionModel(phone=phone, sessionkey=sessionkey)
			db.session.add(S)
			db.session.commit()
			return jsonify({'status':220, 'message':'LoginRedirect', 'session_key':sessionkey})
		#---------------------------------------------------------------------------------------

		return jsonify({'status':200, 'message':'OK'})
	return jsonify({'status':0, 'message':'Incorrect OTP'})


@driver.route("/login/<phone>", methods=['GET', 'POST'])
def login_driver(phone):
	if(request.method == 'POST'):
		data = request.get_json()
		otp = data['otp']
		is_correct = verify_otp(phone, otp)
		if(is_correct):
			#If OTP Verified
			sessionkey = generate_session_id()
			s = SessionModel.query.filter_by(phone=phone).first()
			if(s):
				s.sessionkey = sessionkey
			else:
				s = SessionModel(phone=phone, sessionkey=sessionkey)
				db.session.add(s)
			db.session.commit()
			return jsonify({'status':200, 'message':'OK', 'session_key':sessionkey})
		return jsonify({'status':0, 'message':'Invalid OTP'})
	#On Get request, send OTP to number
	driver = DriverModel.query.filter_by(phone=phone).first()
	if(not driver): return jsonify({'status':0, 'message':'No Driver With that Number'})
	send_otp(phone)
	return jsonify({'status':200, 'message':'OK'})

@driver.route('/logout/<phone>')
def logout_driver(phone):
	S = SessionModel.query.filter_by(phone=phone).first()
	if(not S):  return jsonify({'status':0, 'message':'No Active Session Found'})
	db.session.delete(S)
	db.session.commit()
	return jsonify({'status':200, 'message':'OK'})

@driver.route("/allow_student", methods=['POST'])
def allow_student():
	data = request.get_json()
	sid = data['student_id']
	license_number = data['license_number']
	student = StudentModel.query.filter_by(student_id=sid).first()
	driver = DriverModel.query.filter_by(license_number=license_number).first()
	if(not verify_session_key(request, driver.phone)):
		printlog("session fault")
		return jsonify({'status':0, 'message':'SessionFault'})
	if(not driver):
		printlog("LicenseFault")
		return jsonify({'status':0, 'message':'Invalid License Number'})
	if(not student):
		printlog("Student IDFault")
		return jsonify({'status':0, 'message':'Invalid Student Phone Number'})
	if(not student.is_paid):
		printlog("Student Not Paid")
		return jsonify({'status':0, 'message':'Student Has not Paid'})
	# printlog(f"DriverLocation: {driver.location}    ---->   StudentLocation: {student.location}")
	if(not student.location == driver.location):
		printlog("Locations dont match")
		return jsonify({'status':0, 'message': 'Locations do not match'})
	journey = JourneyModel(driver=driver, student=student)
	db.session.add(journey)
	db.session.commit()
	printlog(f"{driver} Allowed {student}")
	return jsonify({'status':200, 'message':'OK'})

@driver.route("/add_rating", methods=['POST'])
def add_rating():
	data = request.get_json()
	license_number = data['license_number']
	phone = data['student_phone']
	rating = int(data['rating'])
	driver = DriverModel.query.filter_by(license_number=license_number).first()
	student = StudentModel.query.filter_by(phone=phone).first()
	if(not verify_session_key(request, student.phone)): return jsonify({'status':0, 'message':'SessionFault'})
	if(not driver):  return jsonify({'status':0, 'message':'Invalid License Number'})
	if(not student): return jsonify({'status':0, 'message':'Invalid Student Phone Number'})
	if( not any([(J.student == student) for J in driver.journeys]) ):
		return jsonify({'status':0, 'message':'Cannot Rate as Student has not travelled with Driver'})
	driver.add_rating(rating)
	return jsonify({'status':200, 'message':'OK'})

@driver.route("/edit_profile", methods=['POST'])
def edit_profile():
	data = request.get_json()
	id = data['id'] #Identifier
	driver = DriverModel.query.filter_by(id=id).first()
	if(not driver):  return jsonify({'status':0, 'message':'Invalid ID'})

	if(not verify_session_key(request, driver.phone)): return jsonify({'status':0, 'message':'SessionFault'})

	name = data['name'] or driver.name
	phone = data['phone_number'] or driver.phone
	bus_number = data['bus_number'] or driver.bus_number
	experience = data['experience'] or driver.experience
	license_number = data['license_number'] or driver.license_number
	timings = data['timings'] or [] #[[8:30AM, 3:30PM], [7:20AM, 2:20PM]]

	location = driver.location[0]
	location.drivers.remove(driver) #Remove Existing Location
	if(data['location']): 
		location = LocationModel.query.filter_by(location_name=data['location'].lower()).first()
		if(not location):
			loc = LocationModel(location_name=data['location'].lower())
			db.session.add(loc)
			db.session.commit()
			location = loc


	#If such sensitive information changes, Driver must be reverified
	#!REMOVED UNDER SPECIFIC REQUEST BY ISMAIL
	# if(phone != driver.phone or data['bus_number'] != driver.bus_number or data['license_number'] != driver.license_number):
	# 	driver.is_verified = False

	if(phone != driver.phone):
		#Number Changed -> Verify Number
		
		driver.phone_verified = False
		S = SessionModel.query.filter_by(phone=driver.phone).first()
		if(S):
			S.phone = phone
			db.session.commit()
		send_otp(phone)

	if(timings and timings != []):
		timings = list(timings)
		# printlog("Recievedtimings", timings)
		#Remove All Driver's Timings
		driver.timings = []
		db.session.commit()
		#Make new or collect old Timings
		TimingsList = []
		for TList in timings:
			S, E = rectify_timings(TList[0], TList[1])
			T = TimingModel.query.filter_by(start=S, end=E).first()
			if(not T):
				T = TimingModel(start=S, end=E)
				db.session.add(T)
				db.session.commit()
			TimingsList.append(T)

		# printlog("New Timings", TimingsList)
		#Add Timings to Driver
		[T.drivers.append(driver) for T in TimingsList]
		db.session.commit()

	driver.name = name
	driver.phone = phone
	driver.bus_number = bus_number
	driver.experience = experience
	driver.license_number = license_number
	location.drivers.append(driver) #Add Driver to New Location
	db.session.commit()
	return jsonify({'status':200, 'message':'Updated Data'})

@driver.route('/update_profile_image/<phone>', methods=['POST'])
def update_profile_image(phone):
	if(not verify_session_key(request, phone)): return jsonify({'status':0, 'message':'SessionFault'})
	driver = DriverModel.query.filter_by(phone=phone).first()
	if(not driver): return jsonify({'status':0, 'message':'No Driver with that Phone Number'})
	pictureData = request.files['picture']
	pBytes = io.BytesIO(pictureData.read())
	uploaded_img = upload_file_to_cloud(pBytes)
	if(uploaded_img['STATUS'] == 'OK'):
		driver.profile_image = uploaded_img['URI']
	else:
		return jsonify({'status':0, 'message':'Could not Upload image to Cloud (500)'})
	db.session.commit()
	return jsonify({'status':200, 'message':'Updated Profile Image'})


@driver.route('/checkverificationstatus/<number>')
def checkverificationstatus(number):
	if(not verify_session_key(request, number)): return jsonify({'status':0, 'message':'SessionFault'})
	driver = DriverModel.query.filter_by(phone=number).first()
	if(not driver): return jsonify({'status':0, 'message':'No Driver Found with that Phone Number'})

	return jsonify({'status': 200, 'message':'OK', 'isVerified':driver.is_verified})