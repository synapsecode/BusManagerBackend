from flask import Blueprint, jsonify, render_template, request
student = Blueprint('student', __name__)

"""
The student app has these features:

•Accepting agreement.
•User registration with phone number.
• collecting user info like the Area name they stay.
• Monthly subscription through local Payment.
The local payment works like:
- send money to phone number.
- The receiver will get a message saying that he got money from this number 'the sender number'.
So the student, when he send money we just need to know from which number he has sent the money. no need
to integrate like Stripe.


So while we check if we receive the money or not the student will see a loading page or Please wait message.

After the Admin accepts now the student will be able to see available buses to the Area they have entered
while they were registering. and we will provide them an ID "The ID is diff from student Id which university 
gives the student".
"""

@student.route("/")
def student_home():
	return "This is the student module of BusManager"


@student.route("/register", methods=['POST'])
def register_number():
	return f"Registering Number"

@student.route("/login")
def login_number():
	return f"Logging In Number"

@student.route("/paymentstatus/<number>")
def paymentstatus(number):
	return f"Student Has Paid {number}"

@student.route("/getbuses/<number>")
def getbuses(number):
	return jsonify({})