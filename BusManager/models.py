#Database Layer
from datetime import datetime
from flask import current_app
from BusManager import db

location_association = db.Table(
	'LocationAssociations',
	db.Column('location_id', db.Integer, db.ForeignKey('location_model.id')),
	db.Column('driver_id', db.Integer, db.ForeignKey('driver_model.id'))
)

university_association = db.Table(
	'UniversityAssociations',
	db.Column('student_id', db.Integer, db.ForeignKey('student_model.id')),
	db.Column('university_id', db.Integer, db.ForeignKey('university_model.id')),
)

class LocationModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	location_name = db.Column(db.String)
	#Co-ordinates and other stuff

	def __init__(self, location_name):
		self.location_name = location_name

	def __repr__(self):
		return f"Location({self.location_name})"

class DriverModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	phone = db.Column(db.Integer)
	bus_number = db.Column(db.String)
	locations = db.relationship('LocationModel', secondary=location_association, backref=db.backref('drivers', lazy='dynamic'))
	license_number  = db.Column(db.String)
	experience = db.Column(db.Integer) #Accept in terms of years

	def __init__(self, name, phone, bus_number, license_number, experience ):
		self.name = name
		self.phone = phone
		self.bus_number = bus_number
		self.license_number = license_number
		self.experience = experience
		#Add Driver to Location when creating Driver : loc.drivers.append(driver)

	def __repr__(self):
		return f"Driver({self.name}, {self.phone})"

class StudentModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	phone = db.Column(db.Integer)
	student_id = db.Column(db.String)
	home_address = db.Column(db.String)
	university = db.relationship('UniversityModel', secondary=university_association, backref=db.backref('students', lazy='dynamic'))

	def __repr__(self):
		return f"Student({self.name}, {self.phone})"


class UniversityModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)
	#Other University Details