from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()
sched.start()


notif_count = 0
def AutomatedNotificationSender():
	INTERVAL = 2
	LIMIT = 2
	global notif_count
	
	def kill():
		sched.remove_job('autonotif')
		notif_count = 0 #Reset
		print("Done Sending Automated Notifications")

	def work():
		global notif_count
		if(notif_count > LIMIT):
			kill()
			return
		else: notif_count += 1
		print("Created Notification", notif_count)
		

	#Prevent Multiple Calls
	if(len(sched.get_jobs()) == 0):
		notif_count = 0
		sched.add_job(work, 'interval', seconds=INTERVAL, id='autonotif')
		return 200
	else:
		print("Automated Batch Already Running")
		return 42