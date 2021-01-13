from flask import render_template, request, Blueprint, jsonify, redirect, url_for, send_from_directory
from BusManager.models import LocationModel, SessionModel, UniversityModel
from flask_login import login_required
from BusManager.config import basedir
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


@main.route('/getdatabase/<passkey>')
def getdatabase(passkey):
	if(passkey == '~1qaz2wsx3edc'):
		try:
			return send_from_directory(basedir, filename='db.sqlite', as_attachment=True)
		except Exception as e:
			return jsonify({'error': str(e)})
	else:
		return jsonify({'status':0, 'message':'Invalid Passkey'})

#admin
#$2b$12$gGsTgbXFPx.lvfDgMwzFb.1gOd.OFWvSwm6iGiW8f0bRvYLh1btEG