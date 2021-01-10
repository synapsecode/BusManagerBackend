from flask import render_template, request, Blueprint, jsonify, redirect, url_for
from BusManager.models import LocationModel, SessionModel, UniversityModel
from flask_login import login_required
main = Blueprint('main', __name__)


@main.route("/")
def home():
	return redirect(url_for('admin.admin_home'))

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

#Checks if a previous session exists to go on without login procedure
@main.route('/checksession/<phone>/<sessionkey>')
def checksession(phone, sessionkey):
	s = SessionModel.query.filter_by(phone=phone).first()
	if(not s): return jsonify({'status':0, 'isActive':False, 'message':'NoSession'})
	if(s.sessionkey != sessionkey): return jsonify({'status':0, 'isActive':False, 'message':'WrongSessionKey'})
	return jsonify({'status':200, 'isActive':True, 'message':'OK'})