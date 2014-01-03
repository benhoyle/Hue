#!/usr/bin/env python

import imaplib
from email.parser import HeaderParser
import sqlite3 as lite
import datetime
import ConfigParser

def extract_date(word):
	date_index_start = word.find("for ")+4
	date_index_end = word.find(" at")+11
	date_out = word[date_index_start:date_index_end]
	return date_out
	
def extract_sunevent(word):
	#Subject begins with Sunset or Sunrise strip(0:7)
	word_out = word[0:7]
	return word_out.strip()

def read_subjects(label, email_username, email_pw):
	obj = imaplib.IMAP4_SSL('imap.gmail.com', '993')
	obj.login(email_username, email_pw)
	obj.select(label)  # <--- it will select inbox
	typ ,data = obj.search(None,'UnSeen')
	
	subjects =[]
	
	for num in data[0].split():
		data = obj.fetch(num, '(BODY[HEADER])')
		#Mark read email for deletion
		#obj.store(num, '+FLAGS', '\\Deleted') #Need to change imap settings
		header_data = data[1][0][1]
		
		parser = HeaderParser()
		msg = parser.parsestr(header_data)
		#print msg['Subject']
		subjects.append(msg['Subject'])
	
	#Delete read emails
	#obj.expunge() [Need to change settings]
	
	return subjects
	
def storesuninsql(rows, db_path):
	#Save in database
	con = lite.connect(db_path)
	
	with con:
	    
	    cur = con.cursor()   
	     
	    #Create a sun event table if it doesn't already exist
	    cur.execute('CREATE TABLE IF NOT EXISTS sun (r_datetime TIMESTAMP, sunevent TEXT)')
	    
	    for row_values in rows:
	    	#print row_values
	    	#row_values = rows[i]
	    	cur.execute('INSERT INTO sun VALUES(?,?)', (row_values[0], row_values[1]))

def store_sun(subjects, db_path):
#Initilise temporary array for data
	rows = []
	unread_count = len(subjects)
	#print unread_count
	#print subjects
	
	#Process and store unread mail items
	for j in range(0,unread_count):
		#print subjects[j]
		#Extract date/time of sun event
		extracted_date = extract_date(subjects[j])		
		#Extract time of sunevent
		event_time = datetime.datetime.strptime(extracted_date, "%B %d, %Y at %I:%M%p")
		#Extract event name
		event_name = extract_sunevent(subjects[j])
		#Add (event time, event name) tuple to rows
		rows.append((event_time, event_name))
	#print rows
	storesuninsql(rows, db_path)

if __name__ == "__main__":
	#Read settings
	parser = ConfigParser.SafeConfigParser()
	parser.read('config.ini')
	email_username = parser.get('Email Config', 'email_username')
	email_pw = parser.get('Email Config', 'email_pw')
	db_path = parser.get('Path Config', 'db_path')
	
	subjects = read_subjects('Sun', email_username, email_pw)
	store_sun(subjects, db_path)
	
