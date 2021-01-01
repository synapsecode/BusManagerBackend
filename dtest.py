from BusManager import create_app, db
app = create_app()

ac = app.app_context()

def make():
	with ac:
		db.create_all()
		db.session.commit()