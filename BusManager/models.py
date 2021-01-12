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
		self.location_name = location_name.lower()

	def __repr__(self):
		return f"Location({self.location_name})"

class DriverModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	phone = db.Column(db.String)
	bus_number = db.Column(db.String)
	location = db.relationship('LocationModel', secondary=driver_location_association, backref=db.backref('drivers', lazy='dynamic'))
	license_number  = db.Column(db.String)
	experience = db.Column(db.Integer) #Accept in terms of years
	average_rating = db.Column(db.Float) #1-5 Stars (decimal -> resolve in frontend)
	total_ratings = db.Column(db.Integer)
	rating_count = db.Column(db.Integer)
	profile_image = db.Column(db.String) #RawBytes or Hosted Location???
	is_verified = db.Column(db.Boolean)

	phone_verified = db.Column(db.Boolean)

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
		self.phone_verified = False
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
			'id': self.id,
			'name': self.name,
			'phone_number': self.phone,
			'bus_number': self.bus_number,
			'license_number': self.license_number,
			'experience': self.experience,
			'rating': self.average_rating,
			'image': self.profile_image,
			'phone_verified': self.phone_verified,
			'verified': self.is_verified,
			'location': self.location[0].location_name
		}

	def __repr__(self):
		return f"Driver({self.name}, {self.phone})"

class StudentModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	phone = db.Column(db.String)
	student_id = db.Column(db.String)
	home_address = db.Column(db.String)
	university = db.relationship('UniversityModel', secondary=university_association, backref=db.backref('students', lazy='dynamic'))
	is_paid = db.Column(db.Boolean)
	utc_last_paid = db.Column(db.DateTime) #UTCTime of Payment.
	location = db.relationship('LocationModel', secondary=student_location_association, backref=db.backref('students', lazy='dynamic'))

	journeys = db.relationship('JourneyModel', backref='student')

	created_on = db.Column(db.DateTime, default=datetime.utcnow)

	phone_verified = db.Column(db.Boolean)

	#is_lapsed <- Has 6 month period passed?

	def __init__(self, name, phone, student_id, home_address, uni, loc):
		self.name = name
		self.phone = phone
		self.student_id = student_id
		self.home_address = home_address
		uni.students.append(self) #Check if uni exists or else make new one
		loc.students.append(self) #Check if Loc exists or else make new one
		self.is_paid = False
		self.phone_verified = False
		#self.is_lapsed = True

	#Returns true of 6 months (180days have passed since created_on)
	#created_on gets updated everytime student ID is reallocated via admin.
	@property
	def is_lapsed(self):
		if(not self.created_on): return False
		time_delta = (datetime.utcnow() - self.created_on).days
		# print("TimeDelta", time_delta, self.created_on)
		if(time_delta > 180):
			self.is_paid = False
			if(not LapsedStudents.query.filter_by(sid=self.id).first()):
				db.session.add(LapsedStudents(self))
			db.session.commit()
			return True
		return False

	def get_json_representation(self):
		return {
			'id': self.id,
			'name': self.name,
			'phone_number': self.phone,
			'student_id': self.student_id,
			'home_address': self.home_address,
			'university_name': self.university[0].name,
			'university_address': self.university[0].address,
			'phone_verified': self.phone_verified,
			'isPaid': self.is_paid,
			'location': self.location[0].location_name
		}

	def __repr__(self):
		return f"Student({self.name}, {self.phone})"


class UniversityModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	address = db.Column(db.String)

	def __init__(self, name, address):
		self.name = name.lower()
		self.address = address

	def __repr__(self):
		return f"University({self.name})"

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
		return f"Journey({self.driver}->{self.student} @ GMT-{self.timestamp.day}/{self.timestamp.month}/{self.timestamp.year})"


class LapsedStudents(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sid = db.Column(db.Integer)

	def __init__(self, student):
		self.sid = student.id

	@property
	def get_student(self):
		student = StudentModel.query.filter_by(id=self.sid).first()
		return student

	def __repr__(self):
		return self.get_student

class SessionModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	phone = db.Column(db.String)
	sessionkey = db.Column(db.String)

	def __init__(self, phone, sessionkey):
		self.phone = phone
		self.sessionkey = sessionkey

	def __repr__(self):
		return f"Session({self.phone})"

"""
Templates
Driver
	{
		"name":"Noel Fargo",
		"phone_number": "+911111908732",
		"bus_number": "QWER TYUI OP12 3456",
		"location":"Whitefield",
		"license_number":"HGhfhs23nDg332kk",
		"experience": "12"
	}

Student
	{
		"name":"Ruthu Singh",
		"phone_number": "+912221334599",
		"home_address": "#2223 Almagordo Koramangala",
		"location":"Brigade Road",
		"university_name":"Christ PU",
		"university_address": "1333 2nd Cross"
	}

Add Rating
	{
		"license_number":"HGhfhs23nDg332kk",
		"student_phone":"912239001221",
		"rating":"1"
	}

Allow Student
	{
		"student_id":"ZsTIGw",
		"license_number":"hhjshsfhfh774748"
	}

Edit Driver
	{
		"id":1,
		"name":"Noel Fargo",
		"phone_number": "+911111908754",
		"bus_number": "QWER TYUI OP12 3457",
		"location":"Kormangla",
		"license_number":"HGhfhs23nDg332kk",
		"experience": "12"
	}
"""