#!/usr/bin/python3
import sqlite3
import pandas as pd
from flask import Flask
from flask import Markup
from flask import Flask, request, render_template,send_file, Response, redirect, url_for, jsonify
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import json
from dateutil.parser import parse

# df(Pandas): 					['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date'] 
# student(mysqlite_table):		['ID'(PRIMARY KEY,AUTOINCREMENT), 'lastname'(lowercase), 'firstname(lowercase)', 'email'] UNIQUE(lastname,firstname,email)
# professor(mysqlite_table):	['ID'(PRIMARY KEY, AUTOINCREMENT), 'lastname'(lowercase), 'firstname'(lowercase), 'email'] UNIQUE(lastname,firstname,email)
# mentoring(mysqlite_table):	['ID'(PRIMARY, AUTOINCREMENT), 'professor_id'(FOREIGN), 'student_id'(FOREIGN), 'dateAssigned'(NULLABLE), 'endDate'(NULLABLE)] UNIQUE(professor_id,student_id)



class Student:
	def __init__(self, id=None, lastname="",firstname="" , email=""):
		self.id = id
		self.lastname = lastname
		self.firstname = firstname
		self.email = email
		

class Professor:
	def __init__(self, id=None, lastname="", firstname="", email=""):
		self.id = id
		self.lastname = lastname
		self.firstname = firstname
		self.email = email	
		
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
	cursor.execute(sql_command)

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
	cursor.execute(sql_command)

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
	cursor.execute(sql_command)

# Find function student ID by name using SELECT, if nothing found, return string "null", else return int(id)
def findStudentIDByName(lastname,firstname):
	studentLastName = lastname.lower()
	studentFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM student WHERE firstname ="'  + studentFirstName + '" AND lastname = "' + studentLastName + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])


# Find professor ID by name using SELECT,if nothing found, return string "null", else return int(id)
def findProfessorIDByName(lastname,firstname):
	professorLastName = lastname.lower()
	professorFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM professor WHERE firstname ="'  + professorFirstName + '" AND lastname = "' + professorLastName + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"   
	
	for row in rows:
		return(row[0])
		
		
#  Find student name by id using SELECT, return string "null", else return (str(lastname), str(firstname))
def findStudentNameById(cursor,id):
	sql_command = 'SELECT lastname, firstname FROM student WHERE ID = "' + str(id) + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0],row[1])
		
#  Find professor name by id using SELECT, return string "null", else return (str(lastname), str(firstname))
def findProfessorNameById(cursor,id):
	sql_command = 'SELECT lastname, firstname FROM professor WHERE ID = "' + str(id) + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0],row[1])

#  Find professor id by student id using SELECT, return string "null", else return int(id)
def findProfessorByStudentId(id):
	sql_command = 'SELECT professor_id FROM mentoring WHERE student_id = "' + str(id) + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])
	
#  Find student object by student id using SELECT, return string "null", else return student object	
def getStudentObjectById(cursor,id):
	sql_command = 'SELECT * FROM student WHERE ID = "' + str(id) + '";'
	cursor.execute(sql_command)
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


#  Find professor object by professor id using SELECT, return string "null", else return professor object	
def getProfessorObjectById(cursor,id):
	sql_command = 'SELECT * FROM professor WHERE ID = "' + str(id) + '";'
	cursor.execute(sql_command)
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


#   Delete a row in student TABLE by student id, return true if success, else return false
def deleteStudentById(cursor,id):
	sql_command = 'DELETE FROM student WHERE ID = ' + str(id)  + ';'
	try:
		cursor.execute(sql_command)
	except:
		return false
		
	return true
	
#   Delete a row in professor TABLE by student id, return true if success, else return false	
def deleteProfessorById(cursor,id):
	sql_command = 'DELETE FROM professor WHERE ID = ' + str(id)  + ';'
	try:
		cursor.execute(sql_command)
	except:
		return false;

	return true

#   Read all 3 tables and join them together, and load into a Pandas dataframe
#   Organize all the column name and sort the dataframe by professor name
#   Note, the name columns are joined by the format of "Lastname, Firstname"
def readDatabaseIntoDataframe(connection):
	sql_command = """
	SELECT student.firstname as student_firstname, student.lastname as student_lastname, 
	professor.firstname as professor_firstname, professor.lastname as professor_lastname,
	student.email, mentoring.dateAssigned, mentoring.endDate
	FROM mentoring, student, professor 
	WHERE mentoring.student_id = student.ID AND mentoring.professor_id = professor.ID
	"""
	df =  pd.read_sql_query(sql_command, connection)
	df["Student"] =  df["student_lastname"].str.title().str.rstrip().str.lstrip() + ", " + df["student_firstname"].str.title().str.lstrip().str.lstrip()
	df["Professor"] = df["professor_lastname"].str.title().str.lstrip().str.rstrip()
	del df["student_firstname"]
	del df["student_lastname"]
	del df["professor_firstname"]
	del df["professor_lastname"]
	df.rename(columns={"email":"Email", "dateAssigned":"Date Assigned", "endDate": "End Date"}, inplace=True)
	col = ["Professor","Student","Email","Date Assigned","End Date"]
	df = df[col]
	df.sort_values(by=['Professor'],inplace=True)
	connection.close()
	return df

#   Simply read a table into Pandas dataframe
def readTableIntoDataFrame(connection,tableName):
	sql_command = "SELECT * from " + tableName
	df =  pd.read_sql_query(sql_command, connection)
	connection.close()
	return df


# Using pandas to extract the csv file
def readCsvIntoDataframe(filename="TEMP_DATASET.csv"):
	colnames=['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date'] 
	df = pd.read_csv(filename,names=colnames,header=None,encoding = "ISO-8859-1")
	return df

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

		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			#print("student [" + studentArr[i].lower() + " is already in the student table")
			pass

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

		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			#print("professor [" + professorArr[i].lower() + "] is already in the professor table") 
			pass

#  Inserting mentoring table from csv file
def insertToMentoringTableFromCSVFile(df,cursor):
	for i in range(df.shape[0]):
		studentName = str(df.iloc[i].get("Student"))
		professorName = str(df.iloc[i].get("Professor"))
		dateAssigned = str(df.iloc[i].get("Assigned_Date")).strip() 
		try:
			dateTimeObj = parse(dateAssigned)
			dateAssigned = dateTimeObj.strftime("%m/%d/%Y")
		except:
			dateAssigned = "null"
		if(len(studentName.split(',')) > 1):
			student_id = findStudentIDByName(studentName.split(',')[0].lstrip().rstrip().lower(),studentName.split(',')[1].lstrip().rstrip().lower())
		else:
			student_id = findStudentIDByName(studentName,"")
		if(len(professorName.split(',')) > 1):
			professor_id = findProfessorIDByName(professorName.split(',')[0].lstrip().rstrip().lower(),professorName.split(',')[1].lstrip().rstrip().lower())
		else:
			professor_id = findProfessorIDByName(professorName.strip(),"")
		
		sql_command = "INSERT INTO mentoring(professor_id, student_id, dateAssigned, endDate) VALUES "
		sql_command += '("' + str(professor_id) + '", "' + str(student_id) +'", "'+ dateAssigned + '", "null");' 

		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			print(studentName + "] already in Mentoring table. (student has already been assigned).")


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

#   Return the number of row in given table, if tablename is incorrect, return "null", else return int(count)
def numberOfCountInTable(tableName):   
	sql_command = 'SELECT COUNT(*) FROM '+ tableName +';'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return row[0]

#   Return an array which contains: 
#   [(0)number_of_rows_in_student_table,(1)number_of_rows_in_professor_table,(2)number_of_rows_in_mentoring_table,(3)average_student_per_mentor, (4)maximum_number_of_student_allowed_to_assign]
def getAllNumbers():
	margin = 0.35
	returnArr = [numberOfCountInTable('student'),numberOfCountInTable('professor'),numberOfCountInTable('mentoring')]
	averageStudentPerMentor = int(numberOfCountInTable('student')/numberOfCountInTable('professor'))
	maximumStudentPerMentor = int(averageStudentPerMentor * (1+margin))
	
	returnArr.append(averageStudentPerMentor)
	returnArr.append(maximumStudentPerMentor)	
	return returnArr

#   Return the number of student for a professor by using the professor id
#   If professor_id is invalid, return "null", else return int(count)
def getNumberOfStudentForMentorID(professor_id):
	sql_command = 'SELECT COUNT(*) FROM mentoring where professor_id = '+ str(professor_id) + ';'
	cursor.execute(sql_command)
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"

	for row in rows:
		return(row[0])

#   Return a dictionary in format such:
#   {
#		professorName: studentCount  
#	}  
def getProfessorAndStudentNumberInDicionary():
	professorDictionary = {}
	for i in range(1,numberOfCountInTable('professor')+1):
		professorDictionary.update({findProfessorNameById(cursor,i)[0] : getNumberOfStudentForMentorID(i)})
	return professorDictionary

#   Assign a student to mentor by UPDATE using mentor_id and student_id
#   All the error checkings are done in the Flask part
def assignStudentToProfessorById(connection,studentId,professorId,assignDate,endDate):
	sql_command = 'UPDATE mentoring SET professor_id = ' + str(professorId) + ', dateAssigned = "' + str(assignDate) + '", endDate = "' + str(endDate) + '" WHERE student_id = "' + str(studentId)  + '";'
	print(sql_command)
	connection.cursor().execute(sql_command)
	connection.commit()
	

#-------------Main Part For Database-------------------
connection = sqlite3.connect("falcuty_mentor.db")
cursor = connection.cursor()

createStudentTable(cursor)
createProfessorTable(cursor)
createMentoringTable(cursor)

df = readCsvIntoDataframe("faculty_mentor_master_list.csv")
df = removeAndFixDataFrame(df)

insertToStudentTableFromCSVFile(df,cursor)
insertToProfessorTableFromCSVFile(df,cursor)
insertToMentoringTableFromCSVFile(df,cursor)

connection.commit()
#------------------------------------------------------



#------------ flask side -----------------------
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True			# If template change, there is no need to reload the APP
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0			# No caching, only for debugging purposes

@app.route('/')
def index():
	return render_template("index.html")
	
# A route to show all numbers and the tables including the joined table
@app.route('/showall',methods = ['POST', 'GET'])
def showall():
	return render_template("showall.html",
	mentoring_tables=[readDatabaseIntoDataframe(sqlite3.connect("falcuty_mentor.db")).to_html(classes='data',index=False)], 
	student_table=[readTableIntoDataFrame(sqlite3.connect("falcuty_mentor.db"),"student").to_html(classes='data',index=False)],
	professor_table=[readTableIntoDataFrame(sqlite3.connect("falcuty_mentor.db"),"professor").to_html(classes='data',index=False)],
	mentor_table=[readTableIntoDataFrame(sqlite3.connect("falcuty_mentor.db"),"mentoring").to_html(classes='data',index=False)],
	numberForEachTable=getAllNumbers(),
	professorDictionary=getProfessorAndStudentNumberInDicionary())

# The main route for this APP
@app.route('/main_menu',methods = ['POST', 'GET'])
def mainMenu():
	student_table = readTableIntoDataFrame(sqlite3.connect("falcuty_mentor.db"),"student").sort_values(by=['lastname'])
	student_table = student_table['lastname'].str.lstrip().str.title() + ', ' + student_table['firstname'].str.lstrip().str.title()
	
	professor_table = readTableIntoDataFrame(sqlite3.connect("falcuty_mentor.db"),"professor").sort_values(by=['lastname'])
	professor_table = professor_table['lastname'].str.strip().str.title()
	
	professorAndNumberDict = getProfessorAndStudentNumberInDicionary()
	newString = ""
	for professorName,count in professorAndNumberDict.items():
		status = ""
		if count < getAllNumbers()[3]:
			status = "EMPTY"
		elif count >= getAllNumbers()[3] and count < getAllNumbers()[4]:
			status = "ALMOST FULL"
		else:
			status = "FULL"
		newString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count,
			'status': status
		})) + ","
	newString = '[' + newString[:-1] + ']'

	
	return render_template("main_menu.html",student_table=student_table.array, professor_table =professor_table.array, professorJson=newString)

# Update the main_menu page by selecting the element "student_name_input"
@app.route('/update',methods=['POST'])
def update():
	selected = request.form['name'] 
	professorid = findProfessorByStudentId(findStudentIDByName(selected.split(',')[0].lower(),selected.split(',')[1].lstrip().lower()))
	if professorid is not 'null':
		professorname =  getProfessorObjectById(cursor,professorid).lastname
	else:
		professorname =  "None"
	
	studentCountForThisProfessor = getProfessorAndStudentNumberInDicionary()[professorname]
	if studentCountForThisProfessor < getAllNumbers()[3]:
		color = "green"
	elif studentCountForThisProfessor >= getAllNumbers()[3] and studentCountForThisProfessor < getAllNumbers()[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS',"selected_name":selected,'professor_name':professorname.capitalize(),'student_count':getProfessorAndStudentNumberInDicionary()[professorname],'number_color':color})

# Update the main_menu page by selecting the element "mentor_name_input"
@app.route('/update_from_professor_datalist',methods=['POST'])
def update_from_professor_datalist():
	selected = request.form['name']	
	professorname = selected.strip().lower()
	studentCountForThisProfessor = getProfessorAndStudentNumberInDicionary()[professorname]
	if studentCountForThisProfessor < getAllNumbers()[3]:
		color = "green"
	elif studentCountForThisProfessor >= getAllNumbers()[3] and studentCountForThisProfessor < getAllNumbers()[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS','student_count':getProfessorAndStudentNumberInDicionary()[professorname],'number_color':color})


# UPDATE the mentoring table by the assign button
@app.route('/assign_mentor_existed_student',methods=['POST'])
def assign_mentor_existed_student():
	studentName = request.form['studentName'].lower()
	mentorName = request.form['mentorName'].lstrip().rstrip().lower()
	assignDate = request.form['assignDate']
	endDate = request.form['endDate']
	print("student " + studentName + " is assinging to mentor " + mentorName + " assigned date: " + assignDate + " end date" + endDate + ".")
	
	if len(studentName.split(',')) < 2:
		return jsonify({'RESULT':'Student name is not in correct format. For example: "Lastname, Firstname" '})
	
	studentId = findStudentIDByName(studentName.split(',')[0].rstrip().lstrip(),studentName.split(',')[1].rstrip().lstrip())
	professorId = findProfessorIDByName(mentorName,"")
	
	if studentId == "null":
		return jsonify({'RESULT':'Unable to find this student. Try create new student.'})
	
	if professorId == "null":
		return jsonify({'RESULT':"Unable to find this mentor. Please double check this mentor's name."})
	
	if professorId == findProfessorByStudentId(studentId):
		return jsonify({'RESULT':'This student has already been assigned to this mentor.'})
	
	assignStudentToProfessorById(sqlite3.connect("falcuty_mentor.db"),studentId,professorId,assignDate,endDate)
	return jsonify({'RESULT':'SUCCESS'})
	
# No caching, debugging purposes
@app.after_request
def add_header(r):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	r.headers['Cache-Control'] = 'public, max-age=0'
	return r

# Running the app here
if __name__ == '__main__':
	run_simple('localhost', 5000, app,
				use_debugger=True, use_evalex=True)
