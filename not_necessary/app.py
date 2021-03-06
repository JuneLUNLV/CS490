#!/usr/bin/python3
import sqlite3
import pandas as pd
from flask import Flask
from flask import Markup
from flask import Flask, request, render_template,send_file, Response, redirect, url_for, jsonify, send_file
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import json
from dateutil.parser import parse
import os

#Caldwell,Ivan Alexander id 26 repeated
#Robenalt, Evan id 605 repeated
#Chua,Andreana id 144 repeated

# df(Pandas): 					['Professor', 'Student', 'Rebel_Mail', 'Assigned_Date'] 
# student(mysqlite_table):		['ID'(PRIMARY KEY,AUTOINCREMENT), 'lastname'(lowercase), 'firstname(lowercase)', 'email'] UNIQUE(lastname,firstname,email)
# professor(mysqlite_table):	['ID'(PRIMARY KEY, AUTOINCREMENT), 'lastname'(lowercase), 'firstname'(lowercase), 'email'] UNIQUE(lastname,firstname,email)
# mentoring(mysqlite_table):	['ID'(PRIMARY, AUTOINCREMENT), 'professor_id'(FOREIGN), 'student_id'(FOREIGN), 'dateAssigned'(NULLABLE), 'endDate'(NULLABLE)] UNIQUE(professor_id,student_id)




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
	cursor.execute(sql_command)

# Find function student ID by name using SELECT, if nothing found, return string "null", else return int(id)
def findStudentIDByName(cursor,lastname,firstname):
	studentLastName = lastname.lower()
	studentFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM student WHERE firstname ="'  + studentFirstName + '" AND lastname = "' + studentLastName + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])


def findStudentIDByNameAndMail(cursor,lastname,firstname,mail):
	studentLastName = lastname.lower()
	studentFirstName = firstname.lower()
	sql_command = 'SELECT ID FROM student WHERE firstname ="'  + studentFirstName + '" AND lastname = "' + studentLastName + '" AND email = "' + mail +'";'
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

#   Delete a row in student TABLE by student id, return true if success, else return false
def deleteStudentById(cursor,id):
	sql_command = 'DELETE FROM student WHERE ID = ' + str(id)  + ';'
	try:
		cursor.execute(sql_command)
	except:
		return False
		
	return True

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
			print("student [" + studentArr[i].lower() + "] is already in the student table")


#  Find professor id by student id using SELECT, return string "null", else return int(id)
def findProfessorByStudentId(cursor,id):
	sql_command = 'SELECT professor_id FROM mentoring WHERE student_id = "' + str(id) + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0])

def insertNewStudent(curosor,studentLastName,studentFirstName,studentEmail):
        sql_command = "INSERT INTO student(lastname, firstname, email) VALUES "
        sql_command += '("' + studentLastName + '", "' + studentFirstName +'", "' + studentEmail + '");' 

        try:
            cursor.execute(sql_command)
        except sqlite3.IntegrityError:
            return "EXISTED"
        
        student_id = findStudentIDByNameAndMail(cursor,studentLastName,studentFirstName,studentEmail)      
        return student_id

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
	cursor.execute(sql_command)
	rows = cursor.fetchall()

	if len(rows) == 0:
		return "null"   
	
	for row in rows:
		return(row[0])

#  Find professor name by id using SELECT, return string "null", else return (str(lastname), str(firstname))
def findProfessorNameById(cursor,id):
	sql_command = 'SELECT lastname, firstname FROM professor WHERE ID = "' + str(id) + '";'
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	   
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return(row[0],row[1])

	

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
	
#   Delete a row in professor TABLE by student id, return true if success, else return false	
def deleteProfessorById(cursor,id):
	sql_command = 'DELETE FROM professor WHERE ID = ' + str(id)  + ';'
	try:
		cursor.execute(sql_command)
	except:
		return False

	return True

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


#===============================================================================================================================================


# ----------------------------------- Mentoring Database Table Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

class Mentoring:
	def __init__(self, id=None, professor_id="", student_id="", dateAssigned="", endDate="", studentName="",professorName="",studentRebelMail=""):
		self.id = id
		self.professor_id = professor_id
		self.student_id = student_id
		self.dateAssigned = dateAssigned
		self.endDate = endDate
		self.studentName = studentName
		self.professorName = professorName
		self.studentRebelMail = studentRebelMail
        
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
			student_id = findStudentIDByName(cursor,studentName.split(',')[0].lstrip().rstrip().lower(),studentName.split(',')[1].lstrip().rstrip().lower())
		else:
			student_id = findStudentIDByName(cursor,studentName,"")
		if(len(professorName.split(',')) > 1):
			professor_id = findProfessorIDByName(cursor,professorName.split(',')[0].lstrip().rstrip().lower(),professorName.split(',')[1].lstrip().rstrip().lower())
		else:
			professor_id = findProfessorIDByName(cursor,professorName.strip(),"")
		
		sql_command = "INSERT INTO mentoring(professor_id, student_id, dateAssigned, endDate) VALUES "
		sql_command += '("' + str(professor_id) + '", "' + str(student_id) +'", "'+ dateAssigned + '", "null");' 

		try:
			cursor.execute(sql_command)
		except sqlite3.IntegrityError:
			print("Student [" + studentName + "] already in Mentoring table. (student has already been assigned).")

#   Return the number of student for a professor by using the professor id
#   If professor_id is invalid, return "null", else return int(count)
def getNumberOfStudentForMentorID(cursor,professor_id):
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
	for i in range(1,numberOfCountInTable(cursor,'professor')+1):
		professorDictionary.update({findProfessorNameById(cursor,i)[0] : getNumberOfStudentForMentorID(cursor,i)})
	return professorDictionary

#   Assign a student to mentor by UPDATE using mentor_id and student_id
#   All the error checkings are done in the Flask part
def assignExistedStudentToProfessorById(connection,studentId,professorId,assignDate,endDate):
	sql_command = 'UPDATE mentoring SET professor_id = "' + str(professorId) + '", dateAssigned = "' + str(assignDate) + '", endDate = "' + str(endDate) + '" WHERE student_id = "' + str(studentId)  + '";'
	print(sql_command)
	connection.cursor().execute(sql_command)
	connection.commit()
    
def assignNewStudentToProfessorById(connection,studentId,professorId,assignDate,endDate):
    sql_command = "INSERT INTO mentoring(student_id, professor_id, dateAssigned, endDate) VALUES "
    sql_command += '("' + str(studentId) + '", "' + str(professorId) +'", "' + str(assignDate) + '", "' + str(endDate) +  '");' 
    print(sql_command)
    connection.cursor().execute(sql_command)
    connection.commit()  

def massAssign(arr,professorName):
    professorName = professorName.lower()
    professorId = findProfessorIDByName(cursor,professorName,"")
    for i in arr:
        assignFromRelationshipId(connection,i,professorId)

def assignFromRelationshipId(connection,mentoringId,professorId):
    sql_command = 'UPDATE mentoring SET professor_id = "' + str(professorId) + '" WHERE ID = "' + str(mentoringId)  + '";'
    #print(sql_command)
    try:
        connection.cursor().execute(sql_command)
    except Exception as e: 
        print(e)
    connection.commit()   

def findProfessorIdByMentoringId(cursor,relationship_id):
    sql_command = 'SELECT professor_id FROM mentoring where ID = '+ str(relationship_id) + ';'
    cursor.execute(sql_command)
    rows = cursor.fetchall()

    if len(rows) == 0:
        return "null"

    for row in rows:
        return(row[0])  
    
def findStudentIdByRelationshipId(cursor,relationship_id):
    sql_command = 'SELECT student_id FROM mentoring WHERE ID ="'  + str(relationship_id) + '";'
    cursor.execute(sql_command)
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
    
    cursor.execute(sql_command)

def insertDataToOffline_dataTable(connection,data_name,data_value):
    sql_command = "INSERT INTO offline_data(data_name, data_value) VALUES "
    sql_command += '("' + str(data_name) + '", "' + str(data_value) + '");' 

    try:
        connection.cursor().execute(sql_command)
    except sqlite3.IntegrityError:
        return "EXISTED"
    connection.commit()
    return "SUCCESS"
    
def getDataFromOffline_dataTable(cursor,data_name):
    sql_command = 'SELECT data_value FROM offline_data WHERE data_name = "'  + str(data_name) + '";'
    cursor.execute(sql_command)
    rows = cursor.fetchall()
   
    if len(rows) == 0:
            return "null"

    for row in rows:
        return(row[0])  
    
def updateDataFromOffline_dataTable(connection,data_name,data_value):
	sql_command = 'UPDATE offline_data SET data_value= "' + str(data_value)  + '" WHERE data_name = "' + str(data_name)  + '";'
	connection.cursor().execute(sql_command)
	connection.commit()    

#===============================================================================================================================================


# ----------------------------------- Pandas Dataframe Related Code Area ----------------------------------------------------------------
################################################################################################################################################
################################################################################################################################################

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
	df.rename(columns={"email":"Student Rebel Email", "dateAssigned":"Date Assigned", "endDate": "End Date"}, inplace=True)
	col = ["Professor","Student","Student Rebel Email","Date Assigned","End Date"]
	df = df[col]
	df.sort_values(by=['Professor','Student'],inplace=True)
	return df

#   Simply read a table into Pandas dataframe
def readTableIntoDataFrame(connection,tableName):
	sql_command = "SELECT * from " + tableName
	df =  pd.read_sql_query(sql_command, connection)
	return df


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
	cursor.execute(sql_command)
	rows = cursor.fetchall()
	
	if len(rows) == 0:
		return "null"
	
	for row in rows:
		return row[0]

#   Return an array which contains: 
#   [(0)number_of_rows_in_student_table,(1)number_of_rows_in_professor_table,(2)number_of_rows_in_mentoring_table,(3)average_student_per_mentor, (4)maximum_number_of_student_allowed_to_assign]
def getAllNumbers(cursor):
	margin = float(getDataFromOffline_dataTable(cursor,'DOUBLE_margin_for_max_student_count'))
	returnArr = [numberOfCountInTable(cursor,'student'),numberOfCountInTable(cursor,'professor'),numberOfCountInTable(cursor,'mentoring')]
	averageStudentPerMentor = int(numberOfCountInTable(cursor,'student')/numberOfCountInTable(cursor,'professor'))
	maximumStudentPerMentor = int(averageStudentPerMentor * (1+margin))
	
	returnArr.append(averageStudentPerMentor)
	returnArr.append(maximumStudentPerMentor)
	returnArr.append(margin)
	return returnArr


def getStudentsForProfessor(connection):
    df= readDatabaseIntoDataframe(connection)
    professorNames = list(getProfessorAndStudentNumberInDicionary().keys())
    newString = ""
    for i in range(len(professorNames)):    
        professorName = professorNames[i].capitalize()
        df1 = df[df['Professor'] == professorName].sort_values(by=['Student'])
        df1.index = df1.index + 1 
        df1.reset_index(drop=False,inplace=True)
        studentArr = df1['Student'].array.to_numpy().tolist()
        relationshipIdArr = df1['index'].array.to_numpy().tolist()
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

#-------------Main Part For Database-------------------
connection = sqlite3.connect("falcuty_mentor.db")
cursor = connection.cursor()
createStudentTable(cursor)
createProfessorTable(cursor)
createMentoringTable(cursor)
createOfflineDataTable(cursor)

connection.execute("PRAGMA foreign_keys = ON;")

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(THIS_FOLDER, 'faculty_mentor_master_list.csv')
df = readCsvIntoDataframe(csv_file)

insertToStudentTableFromCSVFile(df,cursor)
insertToProfessorTableFromCSVFile(df,cursor)
insertToMentoringTableFromCSVFile(df,cursor)
insertDataToOffline_dataTable(connection,"DOUBLE_margin_for_max_student_count","0.35")

connection.commit()
connection.close()
#------------------------------------------------------       

#------------ flask side -----------------------
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True			# If template change, there is no need to reload the APP
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0			# No caching, only for debugging purposes

@app.route('/')
def index():
	return redirect(url_for("mainMenu"))
	
# A route to show all numbers and the tables including the joined table
@app.route('/showall',methods = ['POST', 'GET'])
def showall():
	return render_template("showall.html",
	mentoring_tables=[readDatabaseIntoDataframe(connection).to_html(classes='data',index=False)], 
	student_table=[readTableIntoDataFrame(connection,"student").to_html(classes='data',index=False)],
	professor_table=[readTableIntoDataFrame(connection,"professor").to_html(classes='data',index=False)],
	mentor_table=[readTableIntoDataFrame(connection,"mentoring").to_html(classes='data',index=False)],
	offline_data_table=[readTableIntoDataFrame(connection,'offline_data').to_html(classes='data',index=False)], 
	numberForEachTable=getAllNumbers(cursor),
	professorDictionary=getProfessorAndStudentNumberInDicionary())

# The main route for this APP
@app.route('/main_menu',methods = ['POST', 'GET'])
def mainMenu():
	professorAndNumberDict = getProfessorAndStudentNumberInDicionary()
	professorJsonString = ""
	for professorName,count in sorted(professorAndNumberDict.items()):
		status = ""
		if count < getAllNumbers(cursor)[3]:
			status = "EMPTY"
		elif count >= getAllNumbers(cursor)[3] and count < getAllNumbers(cursor)[4]:
			status = "ALMOST FULL"
		else:
			status = "FULL"
		professorJsonString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count,
			'status': status
		})) + ","
	professorJsonString = '[' + professorJsonString[:-1] + ']'

	student_table = readTableIntoDataFrame(connection,"student").sort_values(by=['lastname'])
	student_table['duplicated_name'] = student_table.duplicated(subset=['lastname','firstname'], keep=False)
	studentString = ""
	for i in range(student_table.shape[0]):
		duplicated = 0
		if student_table.iloc[i].duplicated_name == True:
			duplicated = 1
		studentString += (json.dumps({
			"studentName":student_table.iloc[i].lastname.title() + ", " + student_table.iloc[i].firstname.title(),
			"relationship_id":findStudentIdByRelationshipId(cursor,student_table.iloc[i].ID),
			'email': student_table.iloc[i].email,
            'duplicated': str(duplicated)
		})) + ","
	studentString = '[' + studentString[:-1] + ']'    


	return render_template("main_menu.html",studentJson=studentString, professorJson=professorJsonString, numberForEachTable=getAllNumbers(cursor))

# Update the main_menu page by selecting the element "student_name_input"
@app.route('/update',methods=['POST'])
def update():
	relationship_id = request.form['relationship_id'] 
	professorid = findProfessorIdByMentoringId(cursor,relationship_id)
	if professorid is not 'null':
		professorname =  getProfessorObjectById(cursor,professorid).lastname
	else:
		professorname =  "None"
	
	studentCountForThisProfessor = getProfessorAndStudentNumberInDicionary()[professorname]
	if studentCountForThisProfessor < getAllNumbers(cursor)[3]:
		color = "green"
	elif studentCountForThisProfessor >= getAllNumbers(cursor)[3] and studentCountForThisProfessor < getAllNumbers(cursor)[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS','professor_name':professorname.capitalize(),'student_count':getProfessorAndStudentNumberInDicionary()[professorname],'number_color':color})

# Update the main_menu page by selecting the element "mentor_name_input"
@app.route('/update_from_professor_datalist',methods=['POST'])
def update_from_professor_datalist():
	selected = request.form['name']	
	professorname = selected.strip().lower()
	studentCountForThisProfessor = getProfessorAndStudentNumberInDicionary()[professorname]
	if studentCountForThisProfessor < getAllNumbers(cursor)[3]:
		color = "green"
	elif studentCountForThisProfessor >= getAllNumbers(cursor)[3] and studentCountForThisProfessor < getAllNumbers(cursor)[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS','student_count':getProfessorAndStudentNumberInDicionary()[professorname],'number_color':color})


# UPDATE the mentoring table by the assign button
@app.route('/assign_mentor_existed_student',methods=['POST','GET'])
def assign_mentor_existed_student():
	studentId = globalMentoring.student_id
	professorId = globalMentoring.professor_id
	studentName = globalMentoring.studentName
	mentorName = globalMentoring.professorName
	assignDate = globalMentoring.assignedDate
	endDate = globalMentoring.endDate
	print("student " + studentName + " is assinged to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
	assignExistedStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
	return jsonify({'RESULT':'ASSIGNED'})

@app.route('/assign_mentor_existed_student_check',methods=['POST','GET'])
def assign_mentor_existed_student_check():
	studentName = request.form['studentName'].lower()
	mentorName = request.form['mentorName'].lstrip().rstrip().lower()
	assignDate = request.form['assignDate']
	endDate = request.form['endDate']
	relationship_id = request.form['relationship_id']
	print("checking condition for: student " + studentName + " is assinging to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
	
	if len(studentName.split(',')) < 2:
		return jsonify({'RESULT':'Student name is not in correct format. For example: "Lastname, Firstname" '})
	
	studentId = findStudentIdByRelationshipId(cursor,relationship_id)
	professorId = findProfessorIDByName(cursor,mentorName,"")
	
	if studentId == "null":
		return jsonify({'RESULT':'Unable to find this student. Try create new student.'})
	
	if professorId == "null":
		return jsonify({'RESULT':"Unable to find this mentor. Please double check this mentor's name."})
	
	if professorId == findProfessorByStudentId(cursor,studentId):
		return jsonify({'RESULT':'This student has already been assigned to this mentor.'})  
    
	globalMentoring.professor_id = professorId
	globalMentoring.student_id = studentId
	globalMentoring.assignedDate = assignDate
	globalMentoring.endDate = endDate
	globalMentoring.studentName = studentName
	globalMentoring.professorName = mentorName
    
	return jsonify({'RESULT':'SUCCESS'})
    
    
@app.route('/assign_mentor_new_stduent',methods=['POST','GET'])
def assign_mentor_new_stduent():
	professorId = globalMentoring.professor_id
	studentName = globalMentoring.studentName
	mentorName = globalMentoring.professorName
	assignDate = globalMentoring.assignedDate
	endDate = globalMentoring.endDate
	studentRebelMail = globalMentoring.studentRebelMail
    
	studentLastName = studentName.split(',')[0].rstrip().lstrip()
	studentFirstName = studentName.split(',')[1].rstrip().lstrip()
    
	print("New student " + studentName + " is assinged to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
	studentId = insertNewStudent(cursor,studentLastName,studentFirstName,studentRebelMail)
	print("Student id from insertNewStudent: " + str(studentId))
	assignNewStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
	return jsonify({'RESULT':'ASSIGNED'})    

@app.route('/assign_mentor_new_stduent_check',methods=['POST','GET'])
def assign_mentor_new_stduent_check():
    studentLastName = request.form['studentLastName'].rstrip().lstrip().lower()
    studentFirstName = request.form['studentFirstName'].rstrip().lstrip().lower()
    mentorName = request.form['mentorName'].rstrip().lstrip().lower()
    assignDate = request.form['assignDate']
    endDate = request.form['endDate']    
    studentRebelMail = request.form['studentRebelMail'].rstrip().lstrip().lower()
    studentName = studentLastName + ", " + studentFirstName

    print("Checking conditions for student  " + studentName + " is assinging to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
    
    student_id = findStudentIDByNameAndMail(cursor,studentLastName,studentFirstName,studentRebelMail)
    if student_id != "null":
        return jsonify({'RESULT':"Student already existed. Try turn off the New Student Switch."})

    professorId = findProfessorIDByName(cursor,mentorName,"")       
    if professorId == "null":
        return jsonify({'RESULT':"Unable to find this mentor. Please double check this mentor's name."})    

    globalMentoring.professor_id = professorId
    globalMentoring.assignedDate = assignDate
    globalMentoring.endDate = endDate
    globalMentoring.studentName = studentName
    globalMentoring.professorName = mentorName 
    globalMentoring.studentRebelMail = studentRebelMail
    
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

@app.route('/mentoring_joined',methods=['POST','GET'])
def mentoring_joined():
	professorAndNumberDict = getProfessorAndStudentNumberInDicionary()
	newString = ""
	for professorName,count in sorted(professorAndNumberDict.items()):
		newString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count
		})) + ","
	newString = '[' + newString[:-1] + ']'
    
	try:
		studentName = request.args.get('username').title()
	except:
		studentName = ""
        
	try:
		email = request.args.get('email').lower().strip()
	except:
		email = ""
    
	return render_template("mentoring_joined.html",
		mentoring_joined_tables=[readDatabaseIntoDataframe(connection).to_html(classes='data',index=False)],
		studentName = studentName, email=email,
		professorJson=newString)
  
@app.route('/apply_settings',methods=['POST'])   
def apply_settings():
    margin = float(request.form['margin'])
    updateDataFromOffline_dataTable(connection,'DOUBLE_margin_for_max_student_count',margin)
    return jsonify({'RESULT':'SUCCESS'}) 

@app.route('/backup_database',methods=['POST','GET'])
def backup_database():
    return render_template("backup_database.html") 

@app.route('/request_for_backup_database')   
def request_for_backup_database():
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(THIS_FOLDER, "falcuty_mentor.db")
    try:
        file = send_file(db_file, as_attachment=True,attachment_filename='UNLV_CS_mentor.db') 
    except Exception as e:
        file = str(e)
    
    return file


@app.route('/multiple_assign_page',methods=['POST','GET'])
def multiple_assign_page():
	professorAndNumberDict = getProfessorAndStudentNumberInDicionary()
	newString = ""
	for professorName,count in sorted(professorAndNumberDict.items()):
		newString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count
		})) + ","
	newString = '[' + newString[:-1] + ']'
	studentForProfessorsJson = getStudentsForProfessor(connection)
    
	return render_template("multiple_assign_page.html",professorJson=newString,studentForProfessorsJson=studentForProfessorsJson)

@app.route('/multiple_assign_request',methods=['POST','GET'])
def multiple_assign_request():
    teacherName = request.form['teacherName']
    relationshipIdArray = request.form.getlist('relationshipIdArray[]')
    massAssign(relationshipIdArray,teacherName)
    return jsonify({'RESULT':'SUCCESS'})

    
# Running the app here
if __name__ == '__main__':
	connection = sqlite3.connect("falcuty_mentor.db")
	connection.execute("PRAGMA foreign_keys = ON;")
	cursor = connection.cursor()
	globalMentoring = Mentoring()
	run_simple('localhost', 5000, app,
				use_debugger=True, use_evalex=True)

