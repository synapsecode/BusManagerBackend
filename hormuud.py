import requests
import json

def send_hormuud_sms(msg, phone):
	uname = "Rafiiqts"
	pwd = "LC01nKQT+woYp92W4A/B1Jty7tsejRma"
	auth_payload = {
		'grant_type': 'password',
		'password': pwd,
		'username':uname
	}
	auth_response = requests.request(
		'POST',
		'https://smsapi.hormuud.com/token',
		data = auth_payload,
		headers = {'content-type': "application/x-www-form-urlencoded"},
	)
	auth_response = json.loads(auth_response.text)
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