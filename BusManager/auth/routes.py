from flask import render_template, request, Blueprint
auth = Blueprint('auth', __name__)

"""
The Admin section:

As an Admin wants to know:
• From which number the student sent the money.
• Checking the driver info.
• How many students are entered each bus with their IDs
"""

@auth.route("/")
def auth_home():
	return "This is the auth module of BusManager"
