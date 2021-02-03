import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = "2999F6CE5AE30B54AA5D7CED1BA566982BAB34BA2814A51CE1875D2C2D88112"
	#Change db.sqlite to env variable to enable as killswitch
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')  #Database path
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	PRODUCTION_MODE = True #This states whether the app runs in DEBUG MODE or not
	PORT_NUMBER = 5000 #Change to Env Variable to enable kill
	HOST='localhost' #Change to env to enable kill
	
	TWILIO_ACCOUNT_SID = 'AC3fa45717b2f301de424eb588892047d7'
	TWILIO_AUTH_TOKEN = 'f163cc27352e8bb99d01c8d02cbd43c7'

	#Somalian SMS Provider
	HORMUUD_USERAME = "Rafiiqts"
	HORMUUD_PASSWORD = "LC01nKQT+woYp92W4A/B1Jty7tsejRma"

	#Ismail's Cloudinary Data
	CLOUDINARY_CONFIG = {
		"api_key": "766698321853973",
		"api_secret": "oDWtlmsEzGf1K2P_2z736DithSw",
		"cloud_name": "dveimvku4"
	}

	DBDOWNLOADPASS = "~1qaz2wsx3edc"
	NUKEPASS = "~1qaz2wsx3edc"
	# NUKEPASS = "~1qaz2wsx3edc"

#------------------------SECRETS------------------
#+12056352635
#Twilio://ai.krustel:M@na$2003
#admin
#$2b$12$gGsTgbXFPx.lvfDgMwzFb.1gOd.OFWvSwm6iGiW8f0bRvYLh1btEG
