from flask import current_app, config
from BusManager.config import Config
# from run import sched
import random
import time
import io
import os
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import time
from BusManager.models import NotificationModel, OTPModel, SessionModel
from BusManager import create_app, db
import datetime
import requests
import json

from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()
sched.start()
# from BusManager.admin.routes import delete_old_notificiations

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

# def send_nexmo_sms(msg, phone):
# 	import nexmo
# 	client = nexmo.Client(key='92efcb6b', secret='cQ1aHUFDjTbz1kzE')
# 	client.send_message({
# 		'from': 'BusManager',
# 		'to': phone,
# 		'text': msg,
# 	})


def generate_session_id():
	cset = [*[str(i) for i in range(0,10)],*[chr(x) for x in range(65,91)], *[chr(x) for x in range(97,123)]]
	session_id = ''.join([random.choice(cset) for _ in range(16)])
	return session_id

otpstorage = {}

def send_twilio_sms(msg, phone):
	cfg = Config()
	from twilio.rest import Client
	import os
	account_sid = cfg.TWILIO_ACCOUNT_SID
	auth_token = cfg.TWILIO_AUTH_TOKEN	
	client = Client(account_sid, auth_token)
	message = client.messages.create(body=msg, from_='+12056352635', to=phone)
	return message.sid

def send_sms(msg, phone):
	print(send_twilio_sms(msg, phone))
	# print(send_hormuud_sms(msg, phone))

def send_hormuud_sms(msg, phone):
	cfg = Config()
	print("\n\n\nHORMUUD USERNAME", Config.HORMUUD_USERAME)
	print("\n\n\nHORMUUD PASSWORD", Config.HORMUUD_PASSWORD)
	print("\n\n\nCFG HORMUUD USERNAME", cfg.HORMUUD_USERAME)
	print("\n\n\nCFG HORMUUD PASSWORD", cfg.HORMUUD_PASSWORD)
	#---------------Getting Access Tokens---------------------
	auth_payload = f"grant_type=password&username={cfg.HORMUUD_USERNAME}&password=${cfg.HORMUUD_PASSWORD}"
	auth_response = requests.request(
		'POST',
		'https://smsapi.hormuud.com/token',
		data = auth_payload,
		headers = {'content-type': "application/x-www-form-urlencoded"},
	)
	auth_response = json.loads(auth_response.text)
	print("Recieved AUTHRES:", auth_response)
	access_token = auth_response['access_token']

	#---------------Send SMS----------------------

	sms_payload = {
		"senderid":"BusManagerService",
		"mobile": phone,
		"message": msg
	}
	sms_response = requests.request(
		'POST',
		'https://smsapi.hormuud.com/api/SendSMS',
		data=json.dumps(sms_payload),
		headers={'Content-Type':'application/json', 'Authorization': 'Bearer ' + access_token},
	)
	sms_response = json.loads(sms_response.text)
	return sms_response

def otp_generator():
	import random
	return random.randint(1000,9999)

def send_otp(phone):
	#?Default: Remove this in production
	# if(phone != '+918904995101'): phone = '+918904995101'

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
	
	# send_sms(otp, phone) #Send the Message
	send_hormuud_sms(otp, phone)
	

#?Essentially We use OTP To verify number
def verify_otp(phone, otp):
	#Default: Remove this in production
	# if(phone != '+918904995101'): phone = '+918904995101'

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

def timeago(sec):
	tx = str(datetime.timedelta(seconds=sec)).split(":")
	hours = int(tx[0])
	minutes = int(tx[1])
	if(minutes == 0):
		return "now"
	return f"""{f"{hours} hour{'s' if hours>1 else ''} " if hours != 0 else ''}{minutes} minute{'s' if minutes>1 else ''} ago"""

def delete_old_notificiations():
	#!Moved Timestamp Data
	#!Recently changed
	dt = datetime.datetime.utcnow()
	timestamp = f"{dt.day}/{dt.month}/{dt.year}"

	#------------------------DELETE OLD NOTIFICATIONS----------------------
	#Get all notifications
	all_notifs = NotificationModel.query.all()
	#Todays notifs
	cond = NotificationModel.timestamp.startswith(timestamp.split(" ")[0])
	todays_notifs = NotificationModel.query.filter(cond).all()

	if(len(all_notifs) > len(todays_notifs)):
		#old notifs
		old_notifs = list(set(all_notifs) - set(todays_notifs))
		[db.session.delete(N) for N in old_notifs]
		db.session.commit()
	#------------------------DELETE OLD NOTIFICATIONS----------------------


#This function automatically sends(Saves) Notifications to the DB
notif_count = 0
def AutomatedNotificationSender():
	ac = create_app().app_context()
	INTERVAL = 1200 #20 Minutes
	LIMIT = 3 #Runs 4 Times
	global notif_count
	
	def kill():
		sched.remove_job('autonotif')
		notif_count = 0 #Reset
		print("Done Sending Automated Notifications")

	def work():
		global notif_count
		if(notif_count > LIMIT):
			kill()
			return
		else: notif_count += 1

		#Do Work
		with ac:
			T = time.localtime()
			dt = datetime.datetime.utcnow()
			timestamp = f"{dt.day}/{dt.month}/{dt.year} {T.tm_hour}:{T.tm_min}"
			message = "Reminder: Pickup time Has Started!"
			sender = "AutomatedReminder"

			delete_old_notificiations(timestamp)

			notification = NotificationModel(
				sender=sender, 
				message=message, 
				timestamp=timestamp
			)
			db.session.add(notification)
			db.session.commit()
		print("Created Notification", notif_count)
		

	#Prevent Multiple Calls
	with ac:
		if(len(sched.get_jobs()) == 0):
			notif_count = 0
			sched.add_job(work, 'interval', seconds=INTERVAL, id='autonotif')
			return 200
		else:
			print("Automated Batch Already Running")
			return 42