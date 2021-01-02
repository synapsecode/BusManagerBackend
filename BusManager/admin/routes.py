from flask import render_template, request, Blueprint
admin = Blueprint('admin', __name__)

"""
The Admin section:

As an Admin wants to know:
• From which number the student sent the money.
• Checking the driver info.
• How many students are entered each bus with their IDs
Basically All the GLobal Information! > FlaskWTF
"""

@admin.route("/")
def admin_home():
	return "This is the admin module of BusManager"
