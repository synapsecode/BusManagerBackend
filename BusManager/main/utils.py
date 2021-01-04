from flask import session

def send_sms(msg, phone):
	from twilio.rest import Client
	import os
	account_sid = 'AC3fa45717b2f301de424eb588892047d7'
	auth_token = 'f163cc27352e8bb99d01c8d02cbd43c7'
	client = Client(account_sid, auth_token)
	message = client.messages.create(body=msg, from_='+12056352635', to=phone)
	print(message.sid)

def otp_generator():
	import random
	return random.randint(1000,9999)

def send_otp(phone):
	#!Pending: Delete After 60s
	otp = otp_generator()
	session[phone] = otp
	send_sms(otp, phone) #Send the Message

def verify_otp(phone, otp):
	print(f"Session OTP: {phone} -> {session.get(phone)} === {otp}")
	if(not session.get(phone)): return False
	if(int(otp) == int(session.get(phone))):
		session.pop(phone, None)
		return True
	return False