from crontab import CronTab
import datetime
import sqlite3 as lite
import ConfigParser

def gettime(sunevent, db_path):
	#sunevent is a string: 'Sunset' or 'Sunrise'
	con = lite.connect(db_path)
		
	#Get last sunset time
	qry = "SELECT r_datetime FROM sun WHERE sunevent='%s' ORDER BY r_datetime DESC LIMIT 1" % sunevent
	cur = con.execute(qry)
	#We can use fetchone() as only one record will be returned
	record = cur.fetchone()
	suneventdt = datetime.datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S")
	
	#Subtract time from sunset; add time to sunrise
	if sunevent == "Sunset":
		time_to_set = suneventdt - datetime.timedelta(minutes=30)
	else:
		time_to_set = suneventdt + datetime.timedelta(minutes=30)
	
	timearray = [time_to_set.hour, time_to_set.minute]
	return timearray

def setcron(timearray, sunevent, script_path, user):
	#timearray input is an array in the form [hour, minute]
	hour = timearray[0]
	minute = timearray[1]
	user_cron = CronTab(user)
	
	if sunevent == "Sunset":
		list = user_cron.find_comment('sunon')
		if not list:
			cmd_string = 'python %sfadeupall.py' % script_path
			job = user_cron.new(command=cmd_string,comment='sunon') 
		else:
			job = list[0]
	else:
		#Sunrise
		list = user_cron.find_comment('sunoff')
		if not list:
			cmd_string = 'python %sfadedownall.py' % script_path
			job = user_cron.new(command=cmd_string, comment='sunoff') 
		else:
			job = list[0]
	job.minute.clear()
	job.hour.clear()
	job.minute.on(minute)
	job.hour.on(hour)
	job.enable()
	user_cron.write()

#Get settings
parser = ConfigParser.SafeConfigParser()
parser.read('config.ini')
db_path = parser.get('Path Config', 'db_path')
script_path = parser.get('Path Config', 'script_path')
user = parser.get('Path Config', 'user')

#Call functions
timearray_ss = gettime("Sunset", db_path)
timearray_sr = gettime("Sunrise", db_path)
setcron(timearray_ss, "Sunset", script_path, user)
setcron(timearray_sr, "Sunrise", script_path, user)



