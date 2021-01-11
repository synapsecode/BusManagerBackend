"""
The student app has these features:

•Accepting agreement.
•User registration with phone number.
• collecting user info like the Area name they stay.
• Monthly subscription through local Payment.
The local payment works like:
- send money to phone number.
- The receiver will get a message saying that he got money from this number 'the sender number'.
So the student, when he send money we just need to know from which number he has sent the money. no need
to integrate like Stripe.


So while we check if we receive the money or not the student will see a loading page or Please wait message.

After the Admin accepts now the student will be able to see available buses to the Area they have entered
while they were registering. and we will provide them an ID "The ID is diff from student Id which university 
gives the student".


> Which Phone Did you send Money > Verify
"""

from flask import Blueprint, jsonify, render_template, request, session
from BusManager.models import *
from BusManager import db
from BusManager.main.utils import generate_session_id, send_otp, send_sms, verify_otp, verify_session_key
import random
import datetime

def generate_student_id(l):
	cset = [*[str(i) for i in range(0,10)],*[chr(x) for x in range(65,91)], *[chr(x) for x in range(97,123)]]
	sid = ''.join([random.choice(cset) for _ in range(l)])
	return sid

student = Blueprint('student', __name__)


@student.route("/")
def student_home():
	return "This is the student module of BusManager"

@student.route("/register", methods=['POST'])
def register_number():
	data = request.get_json()
	name = data['name']
	phone = data['phone_number']
	location = data['location'].lower()
	uni_name = data['name'].lower()
	uni_addr = data['university_address']
	home_addr = data['home_address']

	#Create location if doesnt exist
	loc = LocationModel.query.filter_by(location_name=location).first()
	if(loc == None):
		loc = LocationModel(location_name=location)
		db.session.add(loc)
		db.session.commit()

	#Create University if doesn't exist
	uni = UniversityModel.query.filter_by(name=uni_name).first()
	if(uni == None):
		uni = UniversityModel(name=uni_name, address=uni_addr)
		db.session.add(loc)
		db.session.commit()

	sid = generate_student_id(6)
	print(sid)
	if(StudentModel.query.filter_by(student_id=sid).first()):
		sid = sid[:2] + name[:2] + str(phone)[:2] #Custom Student ID if Clash Occurs

	student = StudentModel(
		name=name,
		phone=phone,
		student_id=sid,
		home_address=home_addr,
		uni=uni,
		loc=loc,
	)

	#send_otp(phone)
	send_otp('+918904995101')
	db.session.add(student)
	db.session.commit()

	return jsonify({'status': 200, 'message': 'Created'})

@student.route('/getstudent/<phone>')
def getstudent(phone):
	if(not verify_session_key(request, phone)): return jsonify({'status':0, 'message':'SessionFault'})
	student = StudentModel.query.filter_by(phone=phone).first()
	if(not student): return jsonify({'status':0, 'message':'No Student With that Phone Number'})
	return jsonify({
		'status':200,
		'message':'OK',
		'student': student.get_json_representation()	
	})

@student.route("/resend_otp/<phone>")
def resend_otp(phone):
	#send_otp(phone)
	send_otp('+918904995101')
	return jsonify({'status':200, 'message':'OK'})

@student.route("/verifyphone/<phone>/<otp>")
def verify_student_otp(phone, otp):
	# sender_phone = phone
	sender_phone = "+918904995101"
	is_correct = verify_otp(sender_phone, otp)
	if(is_correct):
		student = StudentModel.query.filter_by(phone=phone).first()
		if(not student): return jsonify({'status':0, 'message':'No student with that Phone Number'})
		student.phone_verified = True
		db.session.commit()
		return jsonify({'status':200, 'message':'OK'})
	return jsonify({'status':0, 'message':'Incorrect OTP'})

@student.route("/login/<phone>", methods=['GET', 'POST'])
def login_student(phone):
	sender_phone = "+918904995101" #phone
	if(request.method == 'POST'):
		data = request.get_json()
		otp = data['otp']
		is_correct = verify_otp(sender_phone, otp)
		if(is_correct):
			sessionkey = generate_session_id()
			s = SessionModel(phone=phone, sessionkey=sessionkey)
			db.session.add(s)
			db.session.commit()
			return jsonify({'status':200, 'message':'OK', 'session_key':sessionkey})
		return jsonify({'status':0, 'message':'Invalid OTP'})
	#On Get request, send OTP to number
	student = StudentModel.query.filter_by(phone=phone).first()
	if(not student): return jsonify({'status':0, 'message':'No Student With that Number'})
	send_otp('+918904995101')
	#send_otp(phone)
	return jsonify({'status':200, 'message':'OK'})

@student.route('/logout/<phone>')
def logout_student(phone):
	S = SessionModel.query.filter_by(phone=phone).first()
	if(not S):  return jsonify({'status':0, 'message':'No Active Session Found'})
	db.session.delete(S)
	db.session.commit()
	return jsonify({'status':200, 'message':'OK'})


@student.route("/get_available_buses/<phone_number>")
def getbuses(phone_number):
	if(not verify_session_key(request, phone_number)): return jsonify({'status':0, 'message':'SessionFault'})
	student = StudentModel.query.filter_by(phone=phone_number).first()
	if(student):
		s_loc = student.location[0]
		print(s_loc)
		available_drivers = s_loc.drivers.all()
		return jsonify({
				'status': 200,
				'message':'OK',
				'drivers': [driver.get_json_representation() for driver in available_drivers] if (available_drivers) else []
			})
	return jsonify({'status': 0, 'message': 'Student Does not Exist'})


@student.route('/checkpaymentstatus/<number>')
def checkpaymentstatus(number):
	if(not verify_session_key(request, number)): return jsonify({'status':0, 'message':'SessionFault'})
	student = StudentModel.query.filter_by(phone=number).first()
	if(not student): return jsonify({'status':0, 'message':'No Student Found with that Phone Number'})
	
	if(not student.is_paid): return jsonify({'status': 200, 'message':'OK', 'isPaid':False})

	#Check if 6 months lapsed
	if(student.is_lapsed):
		return jsonify({'status': 0, 'message':'6 Months Completed. Please StudentID Must be renewed', 'isPaid':False})

	#Checking if Payment OverDue
	if((datetime.datetime.utcnow() - student.utc_last_paid).days > 30):
		student.is_paid = False
		db.session.commit()
		return jsonify({'status': 0, 'message':'30 Days Elapsed. Please Pay to restore services', 'isPaid':False})
	

	return jsonify({'status': 200, 'message':'OK', 'isPaid':True})


@student.route("/edit_profile", methods=['POST'])
def edit_profile():
	
	data = request.get_json()
	id = data['id'] #Identifier
	student = StudentModel.query.filter_by(id=id).first()
	if(not student):  return jsonify({'status':0, 'message':'No Student With that ID'})


	name = data.get('name') or student.name
	phone = data.get('phone_number') or student.phone
	address = data.get('home_address') or student.home_address

	if(not verify_session_key(request, student.phone)): return jsonify({'status':0, 'message':'SessionFault'})


	location = student.location[0]
	university = student.university[0]

	location.students.remove(student) #Remove Student from Existing Location
	university.students.remove(student) #Remove Student from Existing University


	#Handle Location Changes
	if(data.get('location')): 
		if(LocationModel.query.filter_by(location_name=data['location'].lower()).first()):
			location = LocationModel.query.filter_by(location_name=data['location'].lower()).first()
		else:
			loc = LocationModel(location_name=data['location'])
			db.session.add(loc)
			db.session.commit()
			location = loc

	#Handle University Changes
	if(data.get('university_name') and data.get('university_address')): 
		if(UniversityModel.query.filter_by(name=data['university_name'].lower()).first()):
			university = UniversityModel.query.filter_by(name=data['university_name']).first()
		else:
			uni = UniversityModel(name=data['university_name'], address=data['university_address'].lower())
			db.session.add(uni)
			db.session.commit()
			university = uni
	

	#! If Phone number changes, send OTP and Perform Reverification

	if(data['phone_number'] != student.phone):
		#Number Changed -> Verify Number
		student.phone_verified = False
		#If Session Exists, change phone number
		S = SessionModel.query.filter_by(phone=student.phone).first()
		if(S):
			db.session.delete(S)
			db.session.commit()
		# send_otp(phone)
		# send_otp('+918904995101')
		#On app, show the Verify OTP Screen and send get request to /verifyphone

	student.name = name
	student.phone = phone
	student.home_address = address
	location.students.append(student) #Add Driver to New Location
	university.students.append(student)
	db.session.commit()
	return jsonify({'status':200, 'message':'Updated Data'})


@student.route('/mydrivers/<phone>')
def mydrivers(phone):
	if(not verify_session_key(request, phone)): return jsonify({'status':0, 'message':'SessionFault'})
	student = StudentModel.query.filter_by(phone=phone).first()
	if(not student): return jsonify({'status':0, 'message':'Invalid Student Phone'})
	drivers = []
	for J in JourneyModel.query.filter_by(student=student).all():
		data = {
			'timestamp': J.timestamp,
			'driver': J.driver.get_json_representation()
		}
		drivers.append(data)
	return jsonify({
		'status':200,
		'message':'OK',
		'drivers': drivers
	})

#+12056352635
#Twilio://ai.krustel:M@na$2003