from BusManager import create_app
from BusManager.config import Config

app = create_app()

#!HOST USING TORNADO SEERVER OR SOMETHING IN PRODUCTION	
if __name__ == '__main__':
	#Runs on localhost:8080
	app.run(debug=True)
