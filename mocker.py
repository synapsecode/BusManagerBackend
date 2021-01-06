from BusManager import create_app, db
from BusManager.models import (StudentModel, DriverModel, LocationModel, UniversityModel, JourneyModel)

import random
import string
from faker import Faker

fake = Faker()

ac = create_app().app_context()

mockLocations = [
	"Jayanagar",
	"East End",
	"JP Nagar",
	"Bannerghatta",
	"Koramangala",
	"Arkere"
]

mockUniversities = [
	['Christ University', '298 David Place South Erin, ND 40559'],
	['Paul\'s University', '151 Jacqueline Cape Suite 202 North Jamesshire, PA 90790'],
	['Base PU', '803 Madden Tunnel Suite 353'],
	['RVPU', '22033 Donald Expressway Suite 771']
]

charset = string.ascii_uppercase+string.ascii_lowercase+string.digits

#GeneratorFunctions
numbergen = lambda: '+91'+(''.join([str(random.randint(0,9)) for _ in range(10)]))
licensegen = lambda: ''.join([random.choice(charset) for _ in range(16)])
unigen = lambda: random.choice(mockUniversities)
expgen = lambda: random.randint(1,20)
busnumgen = lambda: ' '.join([''.join([random.choice(string.ascii_uppercase+string.digits) for _ in range(4)]) for _ in range(4)])



def generate_student():
	univ = random.choice(mockUniversities)
	return {
		"name": fake.name(),
		"phone_number": numbergen(),
		"home_address": fake.address().replace('\n', ' '),
		"location": random.choice(mockLocations),
		"university_name":univ[0],
		"university_address": univ[1],
	}

def generate_driver():
	return {
		"name": fake.name(),
		"phone_number": numbergen(),
		"bus_number": busnumgen(),
		"location": random.choice(mockLocations),
		"license_number":licensegen(),
		"experience": expgen(),
	}

def generate_journey():
	students = None
	drivers = None
	with ac:
		students = StudentModel.query.all()
		drivers = DriverModel.query.all()
	return {
		"student_id": random.choice(students).student_id,
		"license_number":random.choice(drivers).license_number
	}