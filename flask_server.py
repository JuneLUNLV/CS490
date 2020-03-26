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
import database_helper as db_helper

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
	mentoring_tables=[db_helper.readDatabaseIntoDataframe(connection).to_html(classes='data',index=False)], 
	student_table=[db_helper.readTableIntoDataFrame(connection,"student").to_html(classes='data',index=False)],
	professor_table=[db_helper.readTableIntoDataFrame(connection,"professor").to_html(classes='data',index=False)],
	mentor_table=[db_helper.readTableIntoDataFrame(connection,"mentoring").to_html(classes='data',index=False)],
	offline_data_table=[db_helper.readTableIntoDataFrame(connection,'offline_data').to_html(classes='data',index=False)], 
	numberForEachTable=db_helper.getAllNumbers(cursor),
	professorDictionary=db_helper.getProfessorAndStudentNumberInDicionary(cursor))

# The main route for this APP
@app.route('/main_menu',methods = ['POST', 'GET'])
def mainMenu():
	professorAndNumberDict = db_helper.getProfessorAndStudentNumberInDicionary(cursor)
	professorJsonString = ""
	for professorName,count in sorted(professorAndNumberDict.items()):
		status = ""
		if count < db_helper.getAllNumbers(cursor)[3]:
			status = "EMPTY"
		elif count >= db_helper.getAllNumbers(cursor)[3] and count < db_helper.getAllNumbers(cursor)[4]:
			status = "ALMOST FULL"
		else:
			status = "FULL"
		professorJsonString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count,
			'status': status
		})) + ","
	professorJsonString = '[' + professorJsonString[:-1] + ']'

	student_table = db_helper.readTableIntoDataFrame(connection,"student").sort_values(by=['lastname'])
	student_table['duplicated_name'] = student_table.duplicated(subset=['lastname','firstname'], keep=False)
	studentString = ""
	for i in range(student_table.shape[0]):
		duplicated = 0
		if student_table.iloc[i].duplicated_name == True:
			duplicated = 1
		studentString += (json.dumps({
			"studentName":student_table.iloc[i].lastname.title() + ", " + student_table.iloc[i].firstname.title(),
			"relationship_id":db_helper.findStudentIdByRelationshipId(cursor,student_table.iloc[i].ID),
			'email': student_table.iloc[i].email,
            'duplicated': str(duplicated)
		})) + ","
	studentString = '[' + studentString[:-1] + ']'    


	return render_template("main_menu.html",studentJson=studentString, professorJson=professorJsonString, numberForEachTable=db_helper.getAllNumbers(cursor))

# Update the main_menu page by selecting the element "student_name_input"
@app.route('/update',methods=['POST'])
def update():
	relationship_id = request.form['relationship_id'] 
	professorid = db_helper.findProfessorIdByMentoringId(cursor,relationship_id)
	if professorid is not 'null':
		professorname =  db_helper.getProfessorObjectById(cursor,professorid).lastname
	else:
		professorname =  "None"
	
	studentCountForThisProfessor = db_helper.getProfessorAndStudentNumberInDicionary(cursor)[professorname]
	if studentCountForThisProfessor < db_helper.getAllNumbers(cursor)[3]:
		color = "green"
	elif studentCountForThisProfessor >= db_helper.getAllNumbers(cursor)[3] and studentCountForThisProfessor < db_helper.getAllNumbers(cursor)[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS','professor_name':professorname.capitalize(),'student_count':db_helper.getProfessorAndStudentNumberInDicionary(cursor)[professorname],'number_color':color})

# Update the main_menu page by selecting the element "mentor_name_input"
@app.route('/update_from_professor_datalist',methods=['POST'])
def update_from_professor_datalist():
	selected = request.form['name']	
	professorname = selected.strip().lower()
	studentCountForThisProfessor = db_helper.getProfessorAndStudentNumberInDicionary(cursor)[professorname]
	if studentCountForThisProfessor < db_helper.getAllNumbers(cursor)[3]:
		color = "green"
	elif studentCountForThisProfessor >= db_helper.getAllNumbers(cursor)[3] and studentCountForThisProfessor < db_helper.getAllNumbers(cursor)[4]:
		color = "yellow"
	else:
		color = "red"
		   
	return jsonify({'RESULT':'SUCCESS','student_count':db_helper.getProfessorAndStudentNumberInDicionary(cursor)[professorname],'number_color':color})


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
	db_helper.assignExistedStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
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
	
	studentId = db_helper.findStudentIdByRelationshipId(cursor,relationship_id)
	professorId = db_helper.findProfessorIDByName(cursor,mentorName,"")
	
	if studentId == "null":
		return jsonify({'RESULT':'Unable to find this student. Try create new student.'})
	
	if professorId == "null":
		return jsonify({'RESULT':"Unable to find this mentor. Please double check this mentor's name."})
	
	if professorId == db_helper.findProfessorByStudentId(cursor,studentId):
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
	studentId = db_helper.insertNewStudent(cursor,studentLastName,studentFirstName,studentRebelMail)
	print("Student id from insertNewStudent: " + str(studentId))
	db_helper.assignNewStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
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
    
    student_id = db_helper.findStudentIDByNameAndMail(cursor,studentLastName,studentFirstName,studentRebelMail)
    if student_id != "null":
        return jsonify({'RESULT':"Student already existed. Try turn off the New Student Switch."})

    professorId = db_helper.findProfessorIDByName(cursor,mentorName,"")       
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
	professorAndNumberDict = db_helper.getProfessorAndStudentNumberInDicionary(cursor)
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
		mentoring_joined_tables=[db_helper.readDatabaseIntoDataframe(connection).to_html(classes='data',index=False)],
		studentName = studentName, email=email,
		professorJson=newString)
  
@app.route('/apply_settings',methods=['POST'])   
def apply_settings():
    margin = float(request.form['margin'])
    db_helper.updateDataFromOffline_dataTable(connection,'DOUBLE_margin_for_max_student_count',margin)
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
	professorAndNumberDict = db_helper.getProfessorAndStudentNumberInDicionary(cursor)
	newString = ""
	for professorName,count in sorted(professorAndNumberDict.items()):
		newString += (json.dumps({
			"professorName":professorName.strip().title(),
			"count":count
		})) + ","
	newString = '[' + newString[:-1] + ']'
	studentForProfessorsJson = db_helper.getStudentsForProfessor(connection)
    
	return render_template("multiple_assign_page.html",professorJson=newString,studentForProfessorsJson=studentForProfessorsJson)

@app.route('/multiple_assign_request',methods=['POST','GET'])
def multiple_assign_request():
    teacherName = request.form['teacherName']
    relationshipIdArray = request.form.getlist('relationshipIdArray[]')
    db_helper.massAssign(connection,relationshipIdArray,teacherName)
    return jsonify({'RESULT':'SUCCESS'})

    
# Running the app here
if __name__ == '__main__':
	connection = sqlite3.connect("falcuty_mentor.db")
	connection.execute("PRAGMA foreign_keys = ON;")
	cursor = connection.cursor()
	globalMentoring = db_helper.Mentoring()
	run_simple('localhost', 5000, app,
				use_debugger=True, use_evalex=True)