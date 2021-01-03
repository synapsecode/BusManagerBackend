from flask import render_template, request, Blueprint, jsonify
from BusManager.models import LocationModel, UniversityModel
main = Blueprint('main', __name__)

@main.route("/")
def main_home():
	return "BusManagerAPI-Prototype<Main>"

#Gets all the Lcoations on the Server for Suggestions
@main.route('/getlocations')
def get_all_locations():
	L = LocationModel.query.all()
	return jsonify({
		'status': 200,
		'message':'OK',
		'locations':[x.location_name for x in L],
	})

#Gets all the universities on the Server for Suggestions
@main.route('/getuniversities')
def get_uni():
	unis = UniversityModel.query.all()
	return jsonify({
		'status': 200,
		'message':'OK',
		'universities': [
			{
				'uni_name': x.name,
				'uni_address': x.address
			} for x in unis
		],
	})