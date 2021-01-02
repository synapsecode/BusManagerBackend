from flask import render_template, request, Blueprint
driver = Blueprint('driver', __name__)

"""
The Driver app works like this:

• Accept the Agreement
• Collect driver information like buss number
•Show loading or Please wait message while the admin is verifying.
• home page with TextField.
• The driver will enter the Studnet ID and check if the student have paid or not.

If the student have paid the driver can allow the student to enter the bus.

When the driver allows the student, automatically sends the student ID to the Admin.
The Admin will see each bus how many students are in with their ID

> Student Can Give Rating Too
"""

@driver.route("/")
def driver_home():
	return "This is the driver module of BusManager"

@driver.route("/register", methods=['POST'])
def driver_register():
	"""
	Name
	Phone Number
	Bus Number
	Location
	License Number
	Experience (Years) > Verifyng
	  > Check Student ID > Allow (or) Don't Allow
	"""
	return "This is the driver module of BusManager"

@driver.route("/login")
def driver_login():
	return "Login"