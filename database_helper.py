#!/usr/bin/python3
import sqlite3
import pandas as pd
from dateutil.parser import parse
import os
import json
import datetime
import inspect
import logging

#logging.basicConfig(filename='sql_commands.log',level=logging.DEBUG)

#Caldwell,Ivan Alexander id 26 repeated
#Robenalt, Evan id 605 repeated
#Chua,Andreana id 144 repeated

# df(Pandas):					['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date'] 

# faculty_mentor.db
#---------------------------------------------
# student(sqlite_table):		['ID'(PRIMARY KEY,AUTOINCREMENT), 'lastname'(lowercase), 'firstname(lowercase)', 'email'] UNIQUE(lastname,firstname,email)
# professor(sqlite_table):	['ID'(PRIMARY KEY, AUTOINCREMENT), 'lastname'(lowercase), 'firstname'(lowercase), 'email'] UNIQUE(lastname,firstname,email)
# mentoring(sqlite_table):	['ID'(PRIMARY, AUTOINCREMENT), 'professor_id'(FOREIGN), 'student_id'(FOREIGN), 'dateAssigned'(NULLABLE), 'endDate'(NULLABLE)] UNIQUE(professor_id,student_id)
# offline_data(sqlite_table): ['ID'(PRIMARY,AUTOINCREMENT), 'data_name','data_value']
# most_recent_mentoring_updates: ['ID'(PRIMARY,AUTOINCREMENT),'mentoring_id'(foreign key referencing id from mentoring), 'modify_date']
#---------------------------------------------

# login.db
#---------------------------------------------
# User(sqlite_table, with sqlalchemy): ['ID'(PRIMARY KEY), 'username'(unqiue,lowercase), 'password']
# User_to_approve(sqlite_table, with sqlalchemy): ['ID'(PRIMARY KEY), 'username'(unique,lowercase), 'password', 'email'(lowercase)]
#---------------------------------------------

# ----------------------------------- Student Database Table Related Code Area ----------------------------------------------------------------
###############################################################################################################################################
###############################################################################################################################################

class Student:
	def __init__(self, id=None, lastname="",firstname="" , email=""):
		self.id = id
		self.lastname = lastname
		self.firstname = firstname
		self.email = email


#--------------Student Table-------------------
#   ID,lastname,firstname,email
def createStudentTable(cursor):
	sql_command_drop_table = """
	DROP TABLE IF EXISTS student;"""
	cursor.execute(sql_command_drop_table)

	sql_command = """
	CREATE TABLE student ( 
	ID INTEGER PRIMARY KEY AUTOINCREMENT ,
	lastname VARCHAR(255) NOT NULL,  
	firstname VARCHAR(255) NOT NULL,
	email VARCHAR(255),
	UNIQUE(lastname,firstname,email)
	);
	"""
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)


# Find function student ID by name using SELECT, if nothing found, return string "null", else return int(id)
def findStudentIDByName(cursor,lastname,firstname):
	studentLastName = lastname.lower()
	studentFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM student WHERE firstname ="'  + studentFirstName + '" AND lastname = "' + studentLastName + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])


def findStudentIDByNameAndMail(cursor,lastname,firstname,mail):
	studentLastName = lastname.lower()
	studentFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM student WHERE firstname ="'  + studentFirstName + '" AND lastname = "' + studentLastName + '" AND email = "' + mail +'";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])

#  Find student name by id using SELECT, return string "null", else return (str(lastname), str(firstname))
def findStudentNameById(cursor,id):
	sql_command = 'SELECT lastname, firstname FROM student WHERE ID = "' + str(id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))

	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0],row[1])

#  Find student object by student id using SELECT, return string "null", else return student object	
def getStudentObjectById(cursor,id):
	sql_command = 'SELECT * FROM student WHERE ID = "' + str(id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"	
		
	student = Student()
	for row in rows:
		student.id = row[0]
		student.lastname = row[1]
		student.firstname = row[2]
		student.email = row[3]
	return student

#   Delete a row in student TABLE by student id, return "SUCESSS" or "FAIL"
def deleteStudentById(connection,id,username):
	sql_command = 'DELETE FROM student WHERE ID = ' + str(id)  + ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)

	# Need to delete the mentoring entry first due to foreign key constraint
	firstResult = deleteMentoringByStudentId(connection,id)
	if firstResult[0] is "FAIL":
		return firstResult
	else:
		try:
			studentObject = getStudentObjectById(connection.cursor(),id)
			connection.cursor().execute(sql_command)
			connection.commit()
			insertOverall_changesTable(connection,username,'student',id,"Student [" + studentObject.lastname.title() + ', ' + studentObject.firstname.title() + "] has been delted.")
		except Exception as e: 
			print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
			logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
			return ("FAIL",str(e))

		return ("SUCCESS","")


# Inserting student table from csv file
def insertToStudentTableFromCSVFile(df,cursor):
	studentArr = df.get("Student")
	studentEmailArr = df.get("Rebel_Mail")
	for i in range(len(studentArr)):
		if ',' in studentArr[i]:
			studentLastName = studentArr[i].split(',')[0].lstrip().rstrip().lower()
			studentFirstName = studentArr[i].split(',')[1].lstrip().rstrip().lower()
		else:
			studentLastName = studentArr[i].lstrip().rstrip().lower()
			studentFirstName = ""
		studentEmail = str(studentEmailArr[i]).strip().lower()

		sql_command = "INSERT INTO student(lastname, firstname, email) VALUES "
		sql_command += '("' + studentLastName + '", "' + studentFirstName +'", "' + studentEmail + '");' 
		#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			print("student [" + studentArr[i].lower() + "] is already in the student table")
			logging.warning("student [" + studentArr[i].lower() + "] is already in the student table")


def insertNewStudent(connection,studentLastName,studentFirstName,studentEmail,username):
	sql_command = "INSERT INTO student(lastname, firstname, email) VALUES "
	sql_command += '("' + studentLastName + '", "' + studentFirstName +'", "' + studentEmail + '");' 
	cursor = connection.cursor()
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
		connection.commit()
		student_id = findStudentIDByNameAndMail(cursor,studentLastName,studentFirstName,studentEmail)	
		insertOverall_changesTable(connection,username,'student',student_id,"New Student [" + studentLastName.title() + ', ' + studentFirstName.title() + "] has been added.")   
	except sqlite3.IntegrityError:
		return "EXISTED"
	except Exception as e:
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return str(e)
	

	return student_id

def updateStudent(connection,student_id,new_student_last_name,new_student_first_name,new_student_email,username):
	oldStudentObject = getStudentObjectById(connection.cursor(),student_id)
	sql_command = 'UPDATE student SET lastname = "' + str(new_student_last_name) + '", firstname = "' + str(new_student_first_name) + '", email = "' + str(new_student_email) + '" WHERE ID = "' + str(student_id)  + '";'
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		msg = "Student [" + oldStudentObject.lastname.title() + ', ' + oldStudentObject.firstname.title() + '] with email [' + oldStudentObject.email + '] has been changed to student name [' + new_student_last_name.title() + ', ' + new_student_first_name.title() + '] with email [' + new_student_email + '].'
		insertOverall_changesTable(connection,username,'student',student_id,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))
	
	return ("SUCCESS","")


#===============================================================================================================================================



# ----------------------------------- Professor Database Table Related Code Area ----------------------------------------------------------------
###############################################################################################################################################
###############################################################################################################################################

class Professor:
	def __init__(self, id=None, lastname="", firstname="", email=""):
		self.id = id
		self.lastname = lastname
		self.firstname = firstname
		self.email = email	
		
#--------------Professor Table-------------------
#   ID,lastname,firstname,email
def createProfessorTable(cursor):
	sql_command_drop_table = """
	DROP TABLE IF EXISTS professor;"""
	cursor.execute(sql_command_drop_table)

	sql_command = """
	CREATE TABLE professor ( 
	ID INTEGER PRIMARY KEY AUTOINCREMENT ,
	lastname VARCHAR(255) NOT NULL,  
	firstname VARCHAR(255) NOT NULL,
	email VARCHAR(255),
	UNIQUE(lastname,firstname,email)
	);
	"""
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)

#dictionary that stores the emails of each professor
professor_email_dict={'bein':'wolfgang.bein@unlv.edu',
					 'berghel':'hlb@acm.org',
					 'datta':'N/A',
					 'gewali':'laxmi.gewali@unlv.edu',
					 'hall':'guymon.hall@unlv.edu',
					 'jo':'juyeon.jo@unlv.edu',
					 'jorgensen':'jorgense@unlv.nevada.edu',
					 'kim':'yoohwan.kim@unlv.edu',
					 'larmore':'lawrence.larmore@unlv.edu',
					 'minor':'john.minor@unlv.edu',
					 'misch':'lee.misch@unlv.edu',
					 'nasoz':'fatma.nasoz@unlv.edu',
					 'pedersen':'matt.pedersen@unlv.edu',
					 'stefik':'andreas.stefik@unlv.edu',
					 'taghva':'kazem.taghva@unlv.edu',
					 'yang':'jisoo.yang@unlv.edu',
					 'yfantis':'evangelos.yfantis@unlv.edu',
					 'zhan':'justin.zhan@unlv.edu',
					 'cacho':'jorge.fonsecacacho@unlv.edu',
					 'vasko':'androvas@unlv.nevada.edu',
					 'dolly':'rudolpha.jorgensen@unlv.edu',
					 'chidella':'kishore.chidella@unlv.edu'}

# Find professor ID by name using SELECT,if nothing found, return string "null", else return int(id)
def findProfessorIDByName(cursor,lastname,firstname):
	professorLastName = lastname.lower()
	professorFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM professor WHERE firstname ="'  + professorFirstName + '" AND lastname = "' + professorLastName + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"   
	
	for row in rows:
		return(row[0])

#  Find professor name by id using SELECT, return string "null", else return (str(lastname), str(firstname))
def findProfessorNameById(cursor,id):
	sql_command = 'SELECT lastname, firstname FROM professor WHERE ID = "' + str(id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return "null"
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0],row[1])

	

#  Find professor object by professor id using SELECT, return string "null", else return professor object	
def getProfessorObjectById(cursor,id):
	sql_command = 'SELECT * FROM professor WHERE ID = "' + str(id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"	

	professor = Professor()
	for row in rows:
		professor.id = row[0]
		professor.lastname = row[1]
		professor.firstname = row[2]
		professor.email = row[3]
	return professor
	
#   Delete a row in professor TABLE by professor id, return "SUCCESS" OR "FAIL"
def deleteProfessorById(connection,id,username):
	sql_command = 'DELETE FROM professor WHERE ID = ' + str(id)  + ';'
	try:
		professorObject = getProfessorObjectById(connection.cursor(),id)
		connection.cursor().execute(sql_command)
		connection.commit()
		msg = 'Professor [' + professorObject.lastname.title() + '] has been deelted.'
		insertOverall_changesTable(connection,username,'professor',id,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))

	return ("SUCCESS","")

# Inserting professor table from csv file
def insertToProfessorTableFromCSVFile(df,cursor):
	professorArr = df.get("Professor")
	for i in range(len(professorArr)):
		if ',' in professorArr[i]:
			professorLastName = professorArr[i].split()[0].lstrip().rstrip().lower()
			professorFirstName = professorArr[i].split()[1].lstrip().rstrip().lower()
		else:
			professorLastName = professorArr[i].split()[0].lstrip().rstrip().lower()
			professorFirstName = ""
		professorEmail = professor_email_dict[professorLastName]

		sql_command = "INSERT INTO professor(lastname, firstname, email) VALUES "
		sql_command += '("' + professorLastName + '", "' + professorFirstName +'", "' + professorEmail + '");' 
		#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			#print("professor [" + professorArr[i].lower() + "] is already in the professor table") 
			pass

def updateMentor(connection,mentor_id,new_mentor_name,new_mentor_email,username):
	oldProfessorObject = getStudentObjectById(connection.cursor(),mentor_id)
	sql_command = 'UPDATE professor SET lastname = "' + str(new_mentor_name) + '", email = "' + str(new_mentor_email) + '" WHERE ID = "' + str(mentor_id)  + '";'
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		msg = "Mentor [" + oldProfessorObject.lastname.title() + ', ' + oldProfessorObject.firstname.title() + '] with email [' + oldProfessorObject.email + '] has been changed to student name [' + new_mentor_name.title() + '] with email [' + new_mentor_email + '].'
		insertOverall_changesTable(connection,username,'professor',mentor_id,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))

	return ("SUCCESS","")


def addMentor(connection,mentor_name,mentor_email,username):
	professorFirstName = ""
	sql_command = "INSERT INTO professor(lastname, firstname, email) VALUES "
	sql_command += '("' + mentor_name + '", "' + professorFirstName +'", "' + mentor_email + '");' 

	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		professor_id = findProfessorIdByNameAndMail(connection.cursor(),mentor_name,mentor_email)
		insertOverall_changesTable(connection,username,'prpfessor',professor_id,"New Professor [" + mentor_name.title() + "] has been added.")
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))	
	return ("SUCCESS","")

def findProfessorIdByNameAndMail(cursor,mentor_name,mentor_email):
	mentor_name = mentor_name.lower()
	sql_command = 'SELECT ID FROM professor WHERE firstname = "" AND lastname = "' + mentor_name + '" AND email = "' + mentor_email +'";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])



#===============================================================================================================================================


# ----------------------------------- Mentoring Database Table Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

class Mentoring:
	def __init__(self, id=None, professor_id="", student_id="", dateAssigned="", endDate="", studentName="",professorName="",studentRebelMail="",relationship_id=""):
		self.id = id
		self.professor_id = professor_id
		self.student_id = student_id
		self.dateAssigned = dateAssigned
		self.endDate = endDate
		self.studentName = studentName
		self.professorName = professorName
		self.studentRebelMail = studentRebelMail
		self.relationship_id = relationship_id
		
#--------------Mentoring Table-------------------
#   ID,professor_id,student_id,dateAssigned,endDate
def createMentoringTable(cursor):
	sql_command_drop_table = """
	DROP TABLE IF EXISTS mentoring;"""
	cursor.execute(sql_command_drop_table)

	sql_command = """
	CREATE TABLE mentoring ( 
	ID INTEGER PRIMARY KEY AUTOINCREMENT ,
	professor_id int NOT NULL,
	student_id int NOT NULL,  
	dateAssigned datetime,
	endDate datetime,
	FOREIGN KEY(professor_id) REFERENCES professor(ID),
	FOREIGN KEY(student_id) REFERENCES student(ID),
	UNIQUE(student_id)
	);
	"""
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)


#  Inserting mentoring table from csv file
def insertToMentoringTableFromCSVFile(df,cursor,isThereEndDate=False):
	for i in range(df.shape[0]):
		studentName = str(df.iloc[i].get("Student"))
		professorName = str(df.iloc[i].get("Professor"))

		dateAssigned = str(df.iloc[i].get("Assigned_Date")).strip() 
		try:
			dateTimeObj = parse(dateAssigned)
			dateAssigned = dateTimeObj.strftime("%m/%d/%Y")
		except Exception as e: 
			dateAssigned = "null"

		endDate = ""
		try:
			endDate = str(df.iloc[i].get("End_Date")).strip()
			dateTimeObj = parse(endDate)
			endDate = dateTimeObj.strftime("%m/%d/%Y")	
		except Exception as e:
			endDate = "null"

		if(len(studentName.split(',')) > 1):
			student_id = findStudentIDByName(cursor,studentName.split(',')[0].lstrip().rstrip().lower(),studentName.split(',')[1].lstrip().rstrip().lower())
		else:
			student_id = findStudentIDByName(cursor,studentName,"")
		if(len(professorName.split(',')) > 1):
			professor_id = findProfessorIDByName(cursor,professorName.split(',')[0].lstrip().rstrip().lower(),professorName.split(',')[1].lstrip().rstrip().lower())
		else:
			professor_id = findProfessorIDByName(cursor,professorName.strip(),"")
		
		sql_command = "INSERT INTO mentoring(professor_id, student_id, dateAssigned, endDate) VALUES "
		if isThereEndDate == False:
			sql_command += '("' + str(professor_id) + '", "' + str(student_id) +'", "'+ dateAssigned + '", "null");' 
		else:
			sql_command += '("' + str(professor_id) + '", "' + str(student_id) +'", "'+ dateAssigned + '", "' + endDate + '");'  
		#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			print("Student [" + studentName + "] already in Mentoring table. (student has already been assigned).")
			logging.warning("Student [" + studentName + "] already in Mentoring table. (student has already been assigned).")

#   Return the number of student for a professor by using the professor id
#   If professor_id is invalid, return "null", else return int(count)
def getNumberOfStudentForMentorID(cursor,professor_id):
	sql_command = 'SELECT COUNT(*) FROM mentoring where professor_id = '+ str(professor_id) + ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"

	for row in rows:
		return(row[0])

#   Return a dictionary in format such:
#   {
#		professorName: studentCount  
#	}  
def getProfessorAndStudentNumberInDicionary(cursor):
	professorDictionary = {}
	maxIdForProfessorTable = maxIdOfTable(cursor,'professor')
	if(maxIdForProfessorTable == "null"):
		return professorDictionary
	
	for i in range(1,maxIdForProfessorTable+1):
		if findProfessorNameById(cursor,i) != "null":
			professorDictionary.update({findProfessorNameById(cursor,i)[0] : getNumberOfStudentForMentorID(cursor,i)})
	return professorDictionary

#   Assign a student to mentor by UPDATE using mentor_id and student_id
#   All the error checkings are done in the Flask part
def assignExistedStudentToProfessorById(connection,studentId,professorId,assignDate,endDate,username):
	sql_command = 'UPDATE mentoring SET professor_id = "' + str(professorId) + '", dateAssigned = "' + str(assignDate) + '", endDate = "' + str(endDate) + '" WHERE student_id = "' + str(studentId)  + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		mentoring_id = findMentoringIdsInArrayByStudentId(connection.cursor(),studentId)[0][0]
		insertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id)
		studentObject = getStudentObjectById(connection.cursor(),studentId)
		professorObject = getProfessorObjectById(connection.cursor(),professorId)
		msg = "Student [" + studentObject.lastname.title() + ', ' + studentObject.firstname.title() +"] has been assigned to professor [" + professorObject.lastname.title() +"]."
		insertOverall_changesTable(connection,username,'mentoring',mentoring_id,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	

	
	
def assignNewStudentToProfessorById(connection,studentId,professorId,assignDate,endDate,username):
	sql_command = "INSERT INTO mentoring(student_id, professor_id, dateAssigned, endDate) VALUES "
	sql_command += '("' + str(studentId) + '", "' + str(professorId) +'", "' + str(assignDate) + '", "' + str(endDate) +  '");' 
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		mentoring_id = findMentoringIdsInArrayByStudentId(connection.cursor(),studentId)[0][0]
		insertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id)
		studentObject = getStudentObjectById(connection.cursor(),studentId)
		professorObject = getProfessorObjectById(connection.cursor(),professorId)
		msg = "New Student [" + studentObject.lastname.title() + ', ' + studentObject.firstname.title() +"] has been assigned to professor [" + professorObject.lastname.title() +"]."
		insertOverall_changesTable(connection,username,'mentoring',mentoring_id,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		


	sql_command = 'SELECT ID FROM mentoring where student_id = '+ str(studentId) + ' AND professor_id = ' + str(professorId) +  ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor = connection.cursor()
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	relationship_id = rows[0][0]
	if(relationship_id != studentId):
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	insertDataToMost_recent_mentoring_updatesTable(connection,relationship_id)
	
	
def massAssign(connection,arr,professorName):
	cursor = connection.cursor()
	professorName = professorName.lower()
	professorId = findProfessorIDByName(cursor,professorName,"")
	currentDT = datetime.datetime.now()
	assignDate = currentDT.strftime("%m/%d/%Y")
	endDate = "null"
	for i in arr:
		assignFromRelationshipId(connection,i,professorId,assignDate,endDate)

def assignFromRelationshipId(connection,mentoringId,professorId,assignDate,endDate,username):
	sql_command = 'UPDATE mentoring SET professor_id = "' + str(professorId) + '", dateAssigned = "' +  str(assignDate) + '" WHERE ID = "' + str(mentoringId)  + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	print(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
		connection.commit()  
		insertDataToMost_recent_mentoring_updatesTable(connection,mentoringId)
		studentId = getStudentIdByMentoringId(connection.cursor(),mentoringId)
		studentObject = getStudentObjectById(connection.cursor(),studentId)
		professorObject = getProfessorObjectById(connection.cursor(),professorId)
		msg = "Student [" + studentObject.lastname.title() + ', ' + studentObject.firstname.title() +"] has been assigned to professor [" + professorObject.lastname.title() +"]."
		insertOverall_changesTable(connection,username,'mentoring',professorId,msg)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))

	

def findProfessorIdByMentoringId(cursor,relationship_id):
	sql_command = 'SELECT professor_id FROM mentoring where ID = '+ str(relationship_id) + ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"

	for row in rows:
		return(row[0])  
	
def findStudentIdByRelationshipId(cursor,relationship_id):
	sql_command = 'SELECT student_id FROM mentoring WHERE ID ="'  + str(relationship_id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"

	for row in rows:
		return(row[0])

#  Find professor id by student id using SELECT, return string "null", else return int(id)
def findProfessorByStudentId(cursor,id):
	sql_command = 'SELECT professor_id FROM mentoring WHERE student_id = "' + str(id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])

def findMentoringIdsInArrayByStudentId(cursor, student_id):
	sql_command = 'SELECT ID FROM mentoring where student_id = "' + str(student_id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	return rows

def findMentoringIdsInArrayByProfessorId(cursor, professor_id):
	sql_command = 'SELECT ID FROM mentoring where professor_id = "' + str(professor_id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	return rows	



#   Delete a row in mentoring TABLE by student id, return "SUCESSS" or "FAIL"
def deleteMentoringByStudentId(connection,student_id):
	temp_cursor = connection.cursor()
	mentoring_id_array = findMentoringIdsInArrayByStudentId(temp_cursor,student_id)
	if mentoring_id_array is "null":
		return ("FAIL","Unable to locate student.")
	for i in mentoring_id_array:
		temp_result = deleteMost_recent_mentoring_updatesByMentoringId(connection,i[0])
		if temp_result[0] is 'FAIL':
			return temp_result

	sql_command = 'DELETE FROM mentoring WHERE student_id = ' + str(student_id)  + ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))

	return ("SUCCESS","")

# def deleteMentoringByProfessorId(connection,professor_id):
# 	temp_cursor = connection.cursor()
# 	mentoring_id_array = findMentoringIdsInArrayByProfessorId(temp_cursor,professor_id)
# 	if mentoring_id_array is "null":
# 		return ("FAIL","Unable to locate professor.")
# 	for i in mentoring_id_array:
# 		temp_result = deleteMost_recent_mentoring_updatesByMentoringId(connection,i[0])
# 		if temp_result[0] is 'FAIL':
# 			return temp_result

# 	sql_command = 'DELETE FROM mentoring WHERE professor_id = ' + str(id)  + ';'
# 	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
# 	try:
# 		connection.cursor().execute(sql_command)
# 		connection.commit()
#
# 	except Exception as e: 
# 		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
# 		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
# 		return ("FAIL",str(e))

# 	return ("SUCCESS","")

def getStudentIdByMentoringId(cursor,mentoring_id):
	sql_command = 'SELECT student_id FROM mentoring where ID = "' + str(mentoring_id) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])



#===============================================================================================================================================


# ----------------------------------- Offline_data Table Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################


#--------------Offline_data Table-------------------
def createOfflineDataTable(cursor):
	sql_command_drop_tbale = '''
	DROP TABLE IF EXISTS offline_data;
	'''
	cursor.execute(sql_command_drop_tbale)
	
	sql_command = '''
	CREATE TABLE offline_data(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	data_name VARCHAR(255) NOT NULL,
	data_value VARCHAR(255) NOT NULL,
	UNIQUE(data_name)
	);
	'''
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)

def insertDataToOffline_dataTable(connection,data_name,data_value):
	sql_command = "INSERT INTO offline_data(data_name, data_value) VALUES "
	sql_command += '("' + str(data_name) + '", "' + str(data_value) + '");' 
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
	except sqlite3.IntegrityError:
		return "EXISTED"
	connection.commit()
	return "SUCCESS"
	
def getDataFromOffline_dataTable(cursor,data_name):
	sql_command = 'SELECT data_value FROM offline_data WHERE data_name = "'  + str(data_name) + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
   
	if len(rows) == 0:
			return "null"

	for row in rows:
		return(row[0])  
	
def updateDataFromOffline_dataTable(connection,data_name,data_value):
	sql_command = 'UPDATE offline_data SET data_value= "' + str(data_value)  + '" WHERE data_name = "' + str(data_name)  + '";'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	connection.commit()	
	# overall_changes_table_insert here

#===============================================================================================================================================

# ----------------------------------- Most_recent_mentoring_updates Table Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

#--------------Most_recent_mentoring_updates Table-------------------
def createMost_recent_mentoring_updatesTable(cursor):
	sql_command_drop_tbale = '''
	DROP TABLE IF EXISTS most_recent_mentoring_updates;
	'''
	cursor.execute(sql_command_drop_tbale)
	
	sql_command = '''
	CREATE TABLE most_recent_mentoring_updates(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	mentoring_id VARCHAR(255) NOT NULL,
	modify_date VARCHAR(255) NOT NULL,
	UNIQUE(mentoring_id),
	FOREIGN KEY(mentoring_id) REFERENCES mentoring(ID)
	);
	'''
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)

def checkAndInsertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id,modify_date):
	sql_command = "INSERT INTO most_recent_mentoring_updates(mentoring_id, modify_date) VALUES "
	sql_command += '("' + str(mentoring_id) + '", "' + str(modify_date) + '");' 
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
	except sqlite3.IntegrityError:
		return False
	connection.commit()
	return True

def deleteDataFromMost_recent_mentoring_updatesTable(connection,mentoring_id):
	sql_command = 'DELETE FROM most_recent_mentoring_updates WHERE mentoring_id = ' + str(mentoring_id)  + ';'
	cursor = connection.cursor()
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		return False
	connection.commit()
	return True

def getMost_recent_mentoring_updatesTableAsDataframeForFlask(connection):

	sql_command = """
	SELECT mentoring.ID as id, student.firstname as student_firstname, student.lastname as student_lastname, 
	professor.firstname as professor_firstname, professor.lastname as professor_lastname,
	student.email, mentoring.dateAssigned, mentoring.endDate, most_recent_mentoring_updates.modify_date as modify_date
	FROM mentoring, student, professor, most_recent_mentoring_updates
	WHERE most_recent_mentoring_updates.mentoring_id = mentoring.ID AND mentoring.student_id = student.ID AND mentoring.professor_id = professor.ID
	"""

	df =  pd.read_sql_query(sql_command, connection)
	df["Student"] =  df["student_lastname"].str.title().str.rstrip().str.lstrip() + ", " + df["student_firstname"].str.title().str.lstrip().str.lstrip()
	df["Professor"] = df["professor_lastname"].str.title().str.lstrip().str.rstrip()
	del df["student_firstname"]
	del df["student_lastname"]
	del df["professor_firstname"]
	del df["professor_lastname"]
	df.rename(columns={"email":"Student Rebel Email", "dateAssigned":"Date Assigned", "endDate": "End Date"}, inplace=True)
	col = ["id","Professor","Student","Student Rebel Email","Date Assigned","End Date","modify_date"]
	df = df[col]
	df.sort_values(by=['Professor','Student'],inplace=True)
	return df

def insertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id):
	currentDT = datetime.datetime.now()
	currentDTString = currentDT.strftime("%m/%d/%Y %H:%M:%S")
	if checkAndInsertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id,currentDTString) == False:
		deleteDataFromMost_recent_mentoring_updatesTable(connection,mentoring_id)
	else:
		return
	checkAndInsertDataToMost_recent_mentoring_updatesTable(connection,mentoring_id,currentDTString)
	

def deleteMost_recent_mentoring_updatesByMentoringId(connection,mentoring_id):
	sql_command = 'DELETE FROM most_recent_mentoring_updates  WHERE mentoring_id = ' + str(mentoring_id)  + ';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))

	return ("SUCCESS","")



# ----------------------------------- overall_changes Database Table Related Code Area ----------------------------------------------------------------
###############################################################################################################################################
###############################################################################################################################################
def createOverall_changesTable(cursor):
	sql_command_drop_tbale = '''
	DROP TABLE IF EXISTS overall_changes;
	'''
	cursor.execute(sql_command_drop_tbale)
	
	sql_command = '''
	CREATE TABLE overall_changes(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	username VARCHAR(255) NOT NULL,
	modify_table VARCHAR(255) NOT NULL,
	modify_id VARCHAR(255),
	message VARCHAR(512),
	modify_date VARCHAR(255)
	);
	'''
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	cursor.execute(sql_command)

def insertOverall_changesTable(connection,username,modify_table,modify_id,message):
	currentDT = datetime.datetime.now()
	currentDTString = currentDT.strftime("%m/%d/%Y %H:%M:%S")
	sql_command = "INSERT INTO overall_changes(username, modify_table, modify_id, message, modify_date) VALUES "
	sql_command += '("' + str(username) + '", "' + str(modify_table) + '", "' + str(modify_id) + '", "' + str(message) + '", "' + str(currentDTString) +'");' 
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		connection.cursor().execute(sql_command)
		connection.commit()
		return ("FAIL","")
	except Exception as e:
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		return ("FAIL",str(e))
	
		 



# ----------------------------------- Pandas DataBase Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

#   Read all 3 tables and join them together, and load into a Pandas dataframe
#   Organize all the column name and sort the dataframe by professor name
#   Note, the name columns are joined by the format of "Lastname, Firstname"
def readDatabaseIntoDataframe(connection, withId = False):
	if withId == False:
		sql_command = """
		SELECT student.firstname as student_firstname, student.lastname as student_lastname, 
		professor.firstname as professor_firstname, professor.lastname as professor_lastname,
		student.email, mentoring.dateAssigned, mentoring.endDate
		FROM mentoring, student, professor 
		WHERE mentoring.student_id = student.ID AND mentoring.professor_id = professor.ID
		"""
	else:
		sql_command = """
		SELECT mentoring.ID as id, student.firstname as student_firstname, student.lastname as student_lastname, 
		professor.firstname as professor_firstname, professor.lastname as professor_lastname,
		student.email, mentoring.dateAssigned, mentoring.endDate
		FROM mentoring, student, professor 
		WHERE mentoring.student_id = student.ID AND mentoring.professor_id = professor.ID
		"""

	df =  pd.read_sql_query(sql_command, connection)
	df["Student"] =  df["student_lastname"].str.title().str.rstrip().str.lstrip() + ", " + df["student_firstname"].str.title().str.lstrip().str.lstrip()
	df["Mentor"] = df["professor_lastname"].str.title().str.lstrip().str.rstrip()
	del df["student_firstname"]
	del df["student_lastname"]
	del df["professor_firstname"]
	del df["professor_lastname"]
	df.rename(columns={"email":"Student Rebel Email", "dateAssigned":"Date Assigned", "endDate": "End Date"}, inplace=True)
	if withId == True:
		col = ["id","Mentor","Student","Student Rebel Email","Date Assigned","End Date"]
	else:
		col = ["Mentor","Student","Student Rebel Email","Date Assigned","End Date"]
	df = df[col]
	df.sort_values(by=['Mentor','Student'],inplace=True)
	return df

#   Simply read a table into Pandas dataframe
def readTableIntoDataFrame(connection,tableName):
	sql_command = "SELECT * from " + tableName
	try:
		df =  pd.read_sql_query(sql_command, connection)
		return df
	except:
		df_empty = pd.DataFrame({'ID' : [], 'empty':[]})
		if tableName is "student" or tableName is "professor":
			df_empty = pd.DataFrame({'ID' : [], 'lastname':[], 'firstname':[], 'email':[]})
		elif tableName is "mentoring":
			df_empty = pd.DataFrame({'ID' : [], 'professor_id':[], 'student_id':[], 'dateAssigned':[],'endDate':[]})
		elif tableName is "most_recent_mentoring_updates":
			df_empty = pd.DataFrame({'ID' : [], 'mentoring_id':[], 'modify_date':[]})
		elif tableName is "offline_data":
			df_empty = pd.DataFrame({'ID' : [], 'data_name':[], 'data_value':[]})
		return df_empty


# Using pandas to extract the csv file
def readCsvIntoDataframe(filename="TEMP_DATASET.csv",originalCVSFile = True):
	if originalCVSFile == True:
		colnames=['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date'] 
	else:
		colnames=['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date', "End_Date"] 
	df = pd.read_csv(filename,names=colnames,header=None,encoding = "ISO-8859-1")
	if originalCVSFile == True:
		df = removeAndFixDataFrame(df)
	return df

#   Remove some row which contains 'ERROR' in student name from dataframe
#   Add "@unlv.nevda.edu" to some incompleted mail  
def removeAndFixDataFrame(df):
	df.drop(df.index[[0,2]],inplace=True)
	ind_drop = df[df['Student'].apply(lambda x: "ERROR" in str(x) or "nan" in str(x))].index
	new_df = df.drop(ind_drop)
	new_df.reset_index(drop=True,inplace=True)
	
	for index,mail in  zip(range(len(new_df['Rebel_Mail'])),new_df['Rebel_Mail']):
		if(type(mail) != float):
			if("@" not in mail):
				new_df.at[index,"Rebel_Mail"] = mail.strip() + "@unlv.nevada.edu"
	
	return new_df

#===============================================================================================================================================

# ----------------------------------- General / Helper Function Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

#   Return the number of row in given table, if tablename is incorrect, return "null", else return int(count)
def numberOfCountInTable(cursor,tableName):   
	sql_command = 'SELECT COUNT(*) FROM '+ tableName +';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return row[0]

def maxIdOfTable(cursor,tableName):   
	sql_command = 'SELECT MAX(ID) FROM '+ tableName +';'
	#logging.debug(inspect.stack()[0][3] + "(): " + sql_command)
	try:
		cursor.execute(sql_command)
	except Exception as e: 
		print("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
		logging.warning("error in "+inspect.stack()[0][3]+"() ! With exception: " + str(e))
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return row[0]



#   Return an array which contains: 
#   [(0)number_of_rows_in_student_table,(1)number_of_rows_in_professor_table,(2)number_of_rows_in_mentoring_table,(3)average_student_per_mentor, (4)maximum_number_of_student_allowed_to_assign]
def getAllNumbers(cursor):
	try:
		margin = float(getDataFromOffline_dataTable(cursor,'DOUBLE_margin_for_max_student_count'))
	except Exception as e: 
		margin = 0
	returnArr = [numberOfCountInTable(cursor,'student'),numberOfCountInTable(cursor,'professor'),numberOfCountInTable(cursor,'mentoring')]
	averageStudentPerMentor = int(numberOfCountInTable(cursor,'student')/numberOfCountInTable(cursor,'professor'))
	maximumStudentPerMentor = int(averageStudentPerMentor * (1+margin))
	
	returnArr.append(averageStudentPerMentor)
	returnArr.append(maximumStudentPerMentor)
	returnArr.append(margin)
	return returnArr


def getStudentsForProfessor(connection):
	df= readDatabaseIntoDataframe(connection,True)
	cursor = connection.cursor()
	professorNames = list(getProfessorAndStudentNumberInDicionary(cursor).keys())
	professorNames
	newString = ""
	for i in range(len(professorNames)):	
		professorName = professorNames[i].capitalize()
		df1 = df[df['Mentor'] == professorName].sort_values(by=['Student'])
		df1.reset_index(drop=False,inplace=True)
		studentArr = df1['Student'].array.to_numpy().tolist()
		relationshipIdArr = df1['id'].array.to_numpy().tolist()
		nameAndIdDictArr = []
		for j in range(len(studentArr)):
			mydict = {
				"studentName":studentArr[j],
				"relationshipId":relationshipIdArr[j]
			}
			nameAndIdDictArr.append(mydict)

		newString += (json.dumps({
			"professorName":professorName,
			"nameAndIdDictArr":nameAndIdDictArr,
		})) + ","
	newString = '[' + newString[:-1] + ']'
	return newString	

		 
#===============================================================================================================================================