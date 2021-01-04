#Database Layer
from datetime import datetime
from flask import current_app
from BusManager import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

class AdminUser(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	password = db.Column(db.String)

	def __repr__(self):
		return f"AdminUser({self.username})"


driver_location_association = db.Table(
	'DriverLocationAssociations',
	db.Column('location_id', db.Integer, db.ForeignKey('location_model.id')),
	db.Column('driver_id', db.Integer, db.ForeignKey('driver_model.id'))
)

student_location_association = db.Table(
	'StudentLocationAssociations',
	db.Column('location_id', db.Integer, db.ForeignKey('location_model.id')),
	db.Column('student_id', db.Integer, db.ForeignKey('student_model.id'))
)

university_association = db.Table(
	'StudentUniversityAssociations',
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
	location = db.relationship('LocationModel', secondary=driver_location_association, backref=db.backref('drivers', lazy='dynamic'))
	license_number  = db.Column(db.String)
	experience = db.Column(db.Integer) #Accept in terms of years
	average_rating = db.Column(db.Float) #1-5 Stars (decimal -> resolve in frontend)
	total_ratings = db.Column(db.Integer)
	rating_count = db.Column(db.Integer)
	profile_image = db.Column(db.String) #RawBytes or Hosted Location???
	is_verified = db.Column(db.Boolean)

	journeys = db.relationship('JourneyModel', backref='driver')
	#affiliated_universities : Basically whichever university they can go to


	def __init__(self, name, phone, bus_number, license_number, experience, loc ):
		self.name = name
		self.phone = phone
		self.bus_number = bus_number
		self.license_number = license_number
		self.experience = experience
		self.average_rating = 0
		self.total_ratings = 0
		self.rating_count = 0
		self.is_verified = False
		self.profile_image = "https://www.ballaratosm.com.au/wp-content/uploads/2018/10/blank-profile.jpg" #Blank Hosted Image
		loc.drivers.append(self)
		#Add Driver to Location when creating Driver : loc.drivers.append(driver)

	def add_rating(self, rating):
		if(rating > 5): return
		self.total_ratings += rating
		self.rating_count += 1
		self.average_rating = (self.total_ratings)/(self.rating_count)
		db.session.commit()

	def get_json_representation(self):
		return {
			'name': self.name,
			'phone': self.phone,
			'bus_number': self.bus_number,
			'license_number': self.license_number,
			'experience': self.experience,
			'rating': self.average_rating,
			'image': self.profile_image
		}

	def __repr__(self):
		return f"Driver({self.name}, {self.phone})"

class StudentModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	phone = db.Column(db.Integer)
	student_id = db.Column(db.String)
	home_address = db.Column(db.String)
	university = db.relationship('UniversityModel', secondary=university_association, backref=db.backref('students', lazy='dynamic'))
	is_paid = db.Column(db.Boolean)
	utc_last_paid = db.Column(db.Float) #UTCTime of Payment.
	location = db.relationship('LocationModel', secondary=student_location_association, backref=db.backref('students', lazy='dynamic'))

	journeys = db.relationship('JourneyModel', backref='student')


	def __init__(self, name, phone, student_id, home_address, uni, loc):
		self.name = name
		self.phone = phone
		self.student_id = student_id
		self.home_address = home_address
		uni.students.append(self) #Check if uni exists or else make new one
		loc.students.append(self) #Check if Loc exists or else make new one
		self.is_paid = False

	def __repr__(self):
		return f"Student({self.name}, {self.phone})"


class UniversityModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)
	#Other University Details


class JourneyModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	driver_id = db.Column(db.Integer, db.ForeignKey('driver_model.id'))
	student_id = db.Column(db.Integer, db.ForeignKey('student_model.id'))
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

	def __init__(self, driver, student):
		self.driver = driver
		self.student = student

	def __repr__(self):
		return f"Journey({driver}->{student} @ GMT-{self.timestamp.day}={self.timestamp.month}-{self.timestamp.year})"