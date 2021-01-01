#Database Layer
from datetime import datetime
from flask import current_app
from BusManager import db

class TestModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	test_name = db.Column(db.String)
