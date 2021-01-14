from BusManager import create_app, db
app = create_app()

ac = app.app_context()

def timing(start, end):
	start = start.upper()
	end = end.upper()
	#Start
	sparts = start.split(':')
	sH = sparts[0].rjust(2, '0')
	sM = sparts[1]
	if(len(sM) == 2):
		sM = f"{sM}{'AM' if(int(sH) < 12) else 'PM'}"
	start = f"{sH}:{sM}"

	eparts = end.split(':')
	eH = eparts[0].rjust(2, '0')
	eM = eparts[1]
	if(len(eM) == 2):
		eM = f"{eM}{'PM' if ((int(eH) < int(sH)) or (int(eH) >= 12)) else 'AM'}"
	end = f"{eH}:{eM}"
	print(start,end)