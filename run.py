from BusManager import create_app
from BusManager.config import Config
# sched = BackgroundScheduler()
# sched.start() #Starting APScheduler
app = create_app()

#!HOST USING TORNADO SEERVER OR SOMETHING IN PRODUCTION	
if __name__ == '__main__':
	app.run(
		debug= Config.PRODUCTION_MODE, 
		port=Config.PORT_NUMBER,
		use_evalex=False,
		host=Config.HOST,
	)
