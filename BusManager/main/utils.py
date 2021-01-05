from flask import session, current_app, config
from BusManager.config import Config
import time

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
	session[phone] = otp
	session[f'T-{phone}'] = int(time.time())
	send_sms(otp, phone) #Send the Message

#?Essentially We use OTP To verify number
def verify_otp(phone, otp):
	TIMEOUT = 60
	ct = int(time.time())
	if(not session.get(phone)): return False
	if(not session.get(f'T-{phone}')): return False
	print(f"Session OTP Req: {phone} -> {session.get(phone)} === {otp} T:{ct - session.get(f'T-{phone}')}s")
	if((ct - session.get(f'T-{phone}') >= TIMEOUT)):
		print("OTP Session Timed Out")
		session.pop(phone, None)
		session.pop(f'T-{phone}', None)
		return False
	if(int(otp) == int(session.get(phone))):
		session.pop(phone, None)
		session.pop(f'T-{phone}', None)
		return True
	return False	