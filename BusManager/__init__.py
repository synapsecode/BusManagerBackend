from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from BusManager.config import Config
from flask_cors import CORS

db = SQLAlchemy()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	CORS(app)

	#Import all your blueprints
	from BusManager.main.routes import main
	from BusManager.auth.routes import auth
	from BusManager.driver.routes import driver
	from BusManager.admin.routes import admin
	from BusManager.student.routes import student
	
	#use the url_prefix arguement if you need prefixes for the routes in the blueprint
	app.register_blueprint(main)
	app.register_blueprint(auth, url_prefix='/auth')
	app.register_blueprint(driver, url_prefix='/driver')
	app.register_blueprint(admin, url_prefix='/admin')
	app.register_blueprint(student, url_prefix='/student')

	return app

#Helper function to create database file directly from terminal
def create_database():
	import BusManager.models
	print("Creating App & Database")
	app = create_app()
	with app.app_context():
		db.create_all()
		db.session.commit()
	print("Successfully Created Database")
