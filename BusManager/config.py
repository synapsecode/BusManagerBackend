import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = "2F5F6CE5AE30B54AA5D7CED1BA566982BAB34BA2814A51CE1865D2C2D8815CD4"
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') #Database path
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	PRODUCTION_MODE = False #This states whether the app runs in DEBUG MODE or not
	PORT_NUMBER = 8080
	DEBUG=True
	
	TWILIO_ACCOUNT_SID = 'AC3fa45717b2f301de424eb588892047d7'
	TWILIO_AUTH_TOKEN = 'f163cc27352e8bb99d01c8d02cbd43c7'

	CLOUDINARY_CONFIG = {
		"api_key": "597356837268799",
		"api_secret": "MgLEKQS1aHJs6TVkGNrv-mfneY0",
		"cloud_name": "krustel-inc"
	}