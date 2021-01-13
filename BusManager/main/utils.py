from flask import current_app, config
from BusManager.config import Config
import random
import time
import io
import os
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import time
from BusManager.models import SessionModel, OTPModel
from BusManager import db

#For Authentication Purposes, After login, the user recieves back a session key.
#This function verifies the session ID.

def verify_session_key(request, phone):
	if('Session-Key' in request.headers):
		skey = request.headers['Session-Key']
		sk = SessionModel.query.filter_by(phone=phone).first()
		if(not sk):
			print("NoSession")
			return False
		if(skey == sk.sessionkey): return True
	return False
	
def upload_file_to_cloud(filebytes, filetype=None):
	try:
		start = time.time()
		# Initialize Variables
		objectURI = ""
		if(filetype != None):
			uploaded_object = upload(filebytes,
									 notification_url="http://localhost",
									 api_key=Config.CLOUDINARY_CONFIG['api_key'],
									 resource_type=str(filetype),
									 api_secret=Config.CLOUDINARY_CONFIG['api_secret'],
									 cloud_name=Config.CLOUDINARY_CONFIG['cloud_name']
									 )
			objectURI = uploaded_object['secure_url']
		else:
			uploaded_object = upload(filebytes,
									 notification_url="http://localhost",
									 api_key=Config.CLOUDINARY_CONFIG['api_key'],
									 api_secret=Config.CLOUDINARY_CONFIG['api_secret'],
									 cloud_name=Config.CLOUDINARY_CONFIG['cloud_name']
									 )
			objectURI = uploaded_object['secure_url']

		end = time.time()
		print(f"TOOK {int(end-start)} seconds to finish")
		return({
			"STATUS": "OK",
			"URI": str(objectURI),
		})
	except Exception as e:
		print("EERRRRRRR", e)
		return({
			"STATUS": "ERR",
			"ERRCODE": str(e)
		})



def generate_session_id():
	cset = [*[str(i) for i in range(0,10)],*[chr(x) for x in range(65,91)], *[chr(x) for x in range(97,123)]]
	session_id = ''.join([random.choice(cset) for _ in range(16)])
	return session_id

otpstorage = {}

def send_sms(msg, phone):
	cfg = Config()
	from twilio.rest import Client
	import os
	account_sid = cfg.TWILIO_ACCOUNT_SID
	auth_token = cfg.TWILIO_AUTH_TOKEN	
	client = Client(account_sid, auth_token)
	message = client.messages.create(body=msg, from_='+12056352635', to=phone)
	print(message.sid)

def otp_generator():
	import random
	return random.randint(1000,9999)

def send_otp(phone):
	otp = otp_generator()
	print(f"OTP -> {otp}")
	T = int(time.time())
	O = OTPModel.query.filter_by(phone=phone).first()
	if(O):
		O.otp = otp
		O.timestamp = T
	else:
		O = OTPModel(phone=phone, otp=otp, timestamp=T)
		db.session.add(O)
	db.session.commit()
	send_sms(otp, phone) #Send the Message

#?Essentially We use OTP To verify number
def verify_otp(phone, otp):
	TIMEOUT = 75
	ct = int(time.time())
	O = OTPModel.query.filter_by(phone=phone).first()
	if(not O): return False
	timedelta = ct - O.timestamp
	print(f"SessionOTPRequest: ({phone} -> {O.otp} === {otp}) : {timedelta}s ")
	ret = False
	if(timedelta >= TIMEOUT):
		print("OTPSessionTimedOut")
	if(int(otp) == O.otp):
		ret = True
	db.session.delete(O)
	db.session.commit()
	return ret	