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

from flask import Blueprint, jsonify, render_template, request
from BusManager.models import UniversityModel, StudentModel, DriverModel, LocationModel
from BusManager import db
from BusManager.main.utils import send_sms, verify_otp, send_otp
import random

def generate_student_id(l):
	#!ID Expires after one month
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
	location = data['location']
	uni_name = data['university_name']
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

	db.session.add(student)
	db.session.commit()

	return jsonify({'status': 200, 'message': 'Created'})

@student.route("/login")
def login_student():
	send_otp('+919611744348')
	return f"Sent OTP"

@student.route("/verifyotp/<otp>")
def verify_student_otp(otp):
	return "Correct" if verify_otp('+919611744348', otp) else "Incorrect"


@student.route("/get_available_buses/<phone_number>")
def getbuses(phone_number):
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



#+12056352635
#Twilio://ai.krustel:M@na$2003