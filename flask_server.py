import sqlite3
import pandas as pd
from flask import Flask
from flask import Markup
from flask import Flask, request, render_template,send_file, Response, redirect, url_for, jsonify, send_file, session
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import json
from dateutil.parser import parse
import os
import database_helper as db_helper
import csvScript
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, fresh_login_required
from urllib.parse import urlparse, urljoin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import shutil
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True			# If template change, there is no need to reload the APP
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0			# No caching, only for debugging purposes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

def get_current_database_folder_path():
    current_database_folder_path = ""
    for x in os.walk(os.getcwd()):
        if "current_database" in x[0]:
            current_database_folder_path = x[0]    
    return current_database_folder_path

def get_csv_folder_path():
    for x in os.walk(os.getcwd()):
        if "csv_folder" in x[0]:
            current_database_folder_path = x[0]    
    return current_database_folder_path 

#FOLDER_PATH = os.path.abspath('')
FOLDER_PATH = get_current_database_folder_path()
        
login_db_file = os.path.join(FOLDER_PATH, 'login.db')   
login_db_file = "sqlite:///" + login_db_file
fileStr = login_db_file

app.config['SQLALCHEMY_DATABASE_URI'] = fileStr
app.config['SECRET_KEY'] = 'da17fb86e4a1121551ac7062aa830e41'
#app.config['USE_SESSION_FOR_NEXT'] = True

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to login!"
login_manager.refresh_view ='login'
login_manager.need_refresh_message = 'You need to re-log in to refresh this page'

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(80))
    
class User_to_approve(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(30))
    applyDate = db.Column(db.String(30))    
    
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,target))
    return test_url.scheme in ('http','https') and \
    ref_url.netloc == test_url.netloc  

def createLoginDb():
    db.create_all()

def signup(username,password):
    new_user = User(username=username,password=password)
    db.session.add(new_user)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] =  587
app.config['MAIL_USERNAME'] = "cs.sys.testing@gmail.com"
app.config['MAIL_PASSWORD'] =  "a474561939"
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)	

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/login')
def login():
    if(current_user.is_authenticated == False):
        session['next'] = request.args.get('next', "/main_menu" )
        return render_template('login.html')        
    else:
        return redirect(url_for("mainMenu"))

@app.route('/login_request',methods=['POST','GET'])
def login_request():
    username = request.form['username'].lstrip().rstrip().lower()
    form_password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        approve_user = User_to_approve.query.filter_by(username=username).first()
        if not approve_user:
            return jsonify({'RESULT':'fail','MSG':'There is no such user.'})
        else:
            return jsonify({'RESULT':'fail','MSG':'This account is waiting to be approved by one of the administrators. Thank you for your patience.'})
    
    if check_password_hash(user.password, form_password):
        login_user(user,remember=True)
    
        if 'next' in session:
            next = session['next']
            
            if is_safe_url(next):
                return jsonify({'RESULT':'SUCCESS','MSG':next})
            else:
                return jsonify({'RESULT':'SUCCESS','MSG':'/main_menu'})
        else:
            return jsonify({'RESULT':'SUCCESS','MSG':'/main_menu'})
    else:
        return jsonify({'RESULT':'FAIL','MSG':'password incorrect.'})
        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/change_password')
@login_required
def change_password():
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username
    return render_template("change_password.html",current_user_name=current_user_name,new_approve_accounts=new_approve_accounts)

@app.route('/change_password_request', methods=['POST','GET'])
def change_password_request():
    new_password = request.form['new_password'] 
    if(current_user.is_authenticated == True):      
        try:
            User.query.filter_by(username=current_user.username).update({"password":generate_password_hash(new_password)})
            db.session.commit()
            return jsonify({'RESULT':'SUCCESS','MSG':'/main_menu'})
        except Exception as e: 
            return jsonify({'RESULT':'FAIL','MSG':str(e)})
    else:
        return jsonify({'RESULT':'FAIL','MSG':'unable to locate user'})
 
@app.route('/delete_account')
@login_required
def delete_account():
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username
    return render_template("delete_account.html",current_user_name=current_user_name,new_approve_accounts=new_approve_accounts)

@app.route('/delete_account_request', methods=['POST','GET'])
def delete_account_request():
    password = request.form['password'] 
    if(current_user.is_authenticated == True): 
        if check_password_hash(current_user.password,password):
            try:
                current_user_username = current_user.username
                logout_user()
                User.query.filter_by(username=current_user_username).delete()
                db.session.commit()
                return jsonify({'RESULT':'SUCCESS','MSG':'/login'})
            except Exception as e: 
                return jsonify({'RESULT':'FAIL','MSG':str(e)})
        else:
            return jsonify({'RESULT':'FAIL','MSG':"password does not match."})
    else:
        return jsonify({'RESULT':'FAIL','MSG':'unable to locate user'})


# A route to show all numbers and the tables including the joined table
@app.route('/showall',methods = ['POST', 'GET'])
@login_required
def showall():
    return render_template("showall.html",
    mentoring_tables=[db_helper.readDatabaseIntoDataframe(connection).to_html(classes='data',index=False)], 
    student_table=[db_helper.readTableIntoDataFrame(connection,"student").to_html(classes='data',index=False)],
    professor_table=[db_helper.readTableIntoDataFrame(connection,"professor").to_html(classes='data',index=False)],
    mentor_table=[db_helper.readTableIntoDataFrame(connection,"mentoring").to_html(classes='data',index=False)],
    offline_data_table=[db_helper.readTableIntoDataFrame(connection,'offline_data').to_html(classes='data',index=False)], 
    most_recent_mentoring_updates_table=[db_helper.readTableIntoDataFrame(connection,'most_recent_mentoring_updates').to_html(classes='data',index=False)],                     
    numberForEachTable=db_helper.getAllNumbers(cursor),
    professorDictionary=db_helper.getProfessorAndStudentNumberInDicionary(cursor),
    new_approve_accounts=new_approve_accounts)

# The main route for this APP
@app.route('/main_menu',methods = ['POST', 'GET'])
@login_required
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
    
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username

    return render_template("main_menu.html",
                           studentJson=studentString, 
                           professorJson=professorJsonString, 
                           numberForEachTable=db_helper.getAllNumbers(cursor), 
                           current_user_name = current_user_name,
                           new_approve_accounts=new_approve_accounts)

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
    relationship_id = globalMentoring.relationship_id
    email_option_checked = request.form['email_option_checked']
    mail_sent = "true"    
    
    mentorEmail = db_helper.getProfessorObjectById(cursor,professorId).email
    studentRebelMail = db_helper.getStudentObjectById(cursor,studentId).email
    
    print("student " + studentName + " is assinged to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
    db_helper.assignExistedStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
    db_helper.insertDataToMost_recent_mentoring_updatesTable(connection,relationship_id) 
#     if email_option_checked == "true":
#         try:
#             msg = Message(subject="Mentor request",
#                           sender=app.config['MAIL_USERNAME'],
#                           recipients=[studentRebelMail],
#                           cc = [],
#                           body="Hi,\nYour faculty mentor is professor " + mentorName.title() + ".  Please email him at"  + mentorEmail + " to schedule an appointment.  Please note, before we can sign the advanced standing form, you will need to have completed your grad plan.  Thanks.\n\n-" + current_user.username)
#             mail.send(msg) 
#             mail_sent = "true"            
#         except Exception as e:
#             mail_sent = "false" 
#             print(str(e))
            
    return jsonify({'RESULT':'ASSIGNED','EMAIL_SENT':mail_sent})
            

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
    globalMentoring.relationship_id = relationship_id
    
    return jsonify({'RESULT':'SUCCESS'})
    
    
@app.route('/assign_mentor_new_stduent',methods=['POST','GET'])
def assign_mentor_new_stduent():
    professorId = globalMentoring.professor_id
    studentName = globalMentoring.studentName
    mentorName = globalMentoring.professorName
    assignDate = globalMentoring.assignedDate
    endDate = globalMentoring.endDate
    studentRebelMail = globalMentoring.studentRebelMail
    email_option_checked = request.form['email_option_checked']
    mail_sent = "true"  
    
    studentLastName = studentName.split(',')[0].rstrip().lstrip()
    studentFirstName = studentName.split(',')[1].rstrip().lstrip()
    
    mentorEmail = db_helper.getProfessorObjectById(cursor,professorId).email
    
    print("New student " + studentName + " is assinged to mentor " + mentorName + " assigned date: " + assignDate + " end date " + endDate + ".")
    studentId = db_helper.insertNewStudent(cursor,studentLastName,studentFirstName,studentRebelMail)
    print("Student id from insertNewStudent: " + str(studentId))
    db_helper.assignNewStudentToProfessorById(connection,studentId,professorId,assignDate,endDate)
    if email_option_checked == "true":
        try:
            msg = Message(subject="Mentor request",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[studentRebelMail],
                          cc = [],
                          body="Hi,\nYour faculty mentor is professor " + mentorName.title() + ".  Please email him at"  + mentorEmail + " to schedule an appointment.  Please note, before we can sign the advanced standing form, you will need to have completed your grad plan.  Thanks.\n\n-" + current_user.username)
            mail.send(msg) 
            mail_sent = "true"            
        except Exception as e:
            mail_sent = "false" 
            print(str(e))
    return jsonify({'RESULT':'ASSIGNED','EMAIL_SENT':mail_sent})    

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
@login_required
def mentoring_joined():
    most_recent_changes_json_string = json.dumps(db_helper.getMost_recent_mentoring_updatesTableAsDataframeForFlask(connection).sort_index(ascending=False).values.tolist())
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
        
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username
        
    return render_template("mentoring_joined.html",
        mentoring_joined_tables=[db_helper.readDatabaseIntoDataframe(connection,True).to_html(classes='data',index=False)],
        studentName = studentName,
        professorJson=newString,
        most_recent_changes_json_string = most_recent_changes_json_string,
        current_user_name = current_user_name,
        new_approve_accounts = new_approve_accounts
        )
  
@app.route('/apply_settings',methods=['POST'])   
def apply_settings():
    margin = float(request.form['margin'])
    db_helper.updateDataFromOffline_dataTable(connection,'DOUBLE_margin_for_max_student_count',margin)
    return jsonify({'RESULT':'SUCCESS'}) 

@app.route('/backup_database',methods=['POST','GET'])
@login_required
def backup_database():
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username       
        
    return render_template("backup_database.html",current_user_name=current_user_name,new_approve_accounts=new_approve_accounts) 

@app.route('/request_for_backup_database')   
def request_for_backup_database():
    FOLDER_PATH = get_current_database_folder_path()     
    falcuty_mentor_db_file = os.path.join(FOLDER_PATH, 'falcuty_mentor.db')  
    try:
        file = send_file(falcuty_mentor_db_file, as_attachment=True,attachment_filename='UNLV_CS_mentor.db') 
    except Exception as e:
        file = str(e)
    
    return file


@app.route('/multiple_assign_page',methods=['POST','GET'])
@login_required
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
    
    current_user_name  = ""    
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username    
    
    return render_template("multiple_assign_page.html",professorJson=newString,studentForProfessorsJson=studentForProfessorsJson,current_user_name=current_user_name,new_approve_accounts=new_approve_accounts)

@app.route('/multiple_assign_request',methods=['POST','GET'])
def multiple_assign_request():
    teacherName = request.form['teacherName']
    relationshipIdArray = request.form.getlist('relationshipIdArray[]')
    db_helper.massAssign(connection,relationshipIdArray,teacherName)
    mail_sent = "true"
    mentor_id = db_helper.findProfessorIDByName(cursor,teacherName.lower(),"")
    mentorEmail = db_helper.getProfessorObjectById(cursor,mentor_id)
    
#     with mail.connect() as conn:
#         for i in relationshipIdArray:
#             student_id = db_helper.findStudentIdByRelationshipId(i)
#             studentRebelMail = db_helper.getStudentObjectById(student_id).email
#             try:
#                 msg = Message(subject="Mentor request",
#                               sender=app.config['MAIL_USERNAME'],
#                               recipients=[studentRebelMail],
#                               cc = [],
#                               body="Hi,\nYour faculty mentor is professor " + teacherName.title() + ".  Please email him at"  + mentorEmail + " to schedule an appointment.  Please note, before we can sign the advanced standing form, you will need to have completed your grad plan.  Thanks.\n\n-" + current_user.username)
#                 mail.send(msg) 
#                 mail_sent = "true"            
#             except Exception as e:
#                 mail_sent = "false" 
#                 print(str(e))
        
    return jsonify({'RESULT':'SUCCESS','EMAIL_SENT':mail_sent})

@app.route('/manage_mentors',methods=['POST','GET'])
@login_required
def manage_mentors():
    current_user_name  = ""    
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username      
        
    df = db_helper.readTableIntoDataFrame(connection,'professor')
    df["Professor"] = df["lastname"].str.title().str.lstrip().str.rstrip()
    del df["lastname"]
    del df["firstname"]
    df = df.rename(columns={"email":"Professor Email"})
    col = ["ID","Professor","Professor Email"]
    df=df[col]
    df["Student Numbers"] = list(db_helper.getProfessorAndStudentNumberInDicionary(cursor).values())
    df.sort_values(by=["Professor"],inplace=True)
    
    return render_template("manage_mentors.html",current_user_name=current_user_name,mentor_2d_array = df.values,new_approve_accounts=new_approve_accounts)

@app.route('/manage_students',methods=['POST','GET'])
@login_required
def manage_students():
    current_user_name  = ""    
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username      
        
    df = db_helper.readTableIntoDataFrame(connection,'student')
    df["Student Last Name"] = df["lastname"].str.title().str.lstrip().str.rstrip()
    df["Student First Name"] = df["firstname"].str.title().str.lstrip().str.rstrip()
    del df["lastname"]
    del df["firstname"]
    df = df.rename(columns={"email":"Student Rebel Mail"})
    col = ["ID","Student Last Name","Student First Name","Student Rebel Mail"]
    df=df[col]
    df.sort_values(by=["Student Last Name","Student First Name"],inplace=True)
    
    return render_template("manage_students.html",current_user_name=current_user_name,student_2d_array = df.values,new_approve_accounts=new_approve_accounts)



@app.route('/update_mentor',methods=['POST','GET'])
def update_mentor():
    mentor_id = request.form['mentor_id']
    new_mentor_name = request.form['new_mentor_name']
    new_mentor_email = request.form['new_mentor_email']
    new_mentor_name = new_mentor_name.lstrip().rstrip().lower()
    new_mentor_email = new_mentor_email.lstrip().rstrip().lower()
    
    result = db_helper.updateMentor(connection,mentor_id,new_mentor_name,new_mentor_email)
    return jsonify({'RESULT':result[0],'MSG':result[1]})
    
@app.route('/delete_mentor',methods=['POST','GET'])
def delete_mentor():
    mentor_id = request.form['mentor_id']
    student_count = db_helper.getNumberOfStudentForMentorID(cursor,mentor_id)
    if student_count is not "null":
        if student_count > 0:
            return jsonify({'RESULT':"FAIL",'MSG':'please make sure this mentor has no students before deleting this mentor.'})
        else:
            result = db_helper.deleteProfessorById(connection,mentor_id)
            return jsonify({'RESULT':result[0],'MSG':result[1]})
    else:
        return jsonify({'RESULT':"FAIL",'MSG':'Unable to find mentor.'})
    
@app.route('/update_student',methods=['POST','GET'])
def update_student():
    student_id = request.form['student_id']
    new_student_last_name = request.form['new_student_last_name']
    new_student_first_name = request.form['new_student_first_name']
    new_student_email = request.form['new_student_email']
    new_student_last_name = new_student_last_name.lstrip().rstrip().lower()
    new_student_first_name = new_student_first_name.lstrip().rstrip().lower()
    new_student_email = new_student_email.lstrip().rstrip().lower()
    
    result = db_helper.updateStudent(connection,student_id,new_student_last_name,new_student_first_name,new_student_email)
    return jsonify({'RESULT':result[0],'MSG':result[1]})
    
@app.route('/delete_student',methods=['POST','GET'])
def delete_student():
    student_id = request.form['student_id']
    result = db_helper.deleteStudentById(connection,student_id)
    return jsonify({'RESULT':result[0],'MSG':result[1]})

                
@app.route('/add_mentor',methods=['POST','GET'])
def add_mentor():
    mentor_name = request.form['mentor_name'].lstrip().rstrip().lower()
    mentor_email = request.form['mentor_email'].lstrip().rstrip().lower()
    print(mentor_name + ": " + mentor_email)
    result = db_helper.addMentor(connection,mentor_name,mentor_email)
    return jsonify({'RESULT':result[0],'MSG':result[1]})
        
@app.route('/restore_database',methods=['POST','GET'])
@login_required
def restore_database():
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username       
        
    return render_template("restore_database.html",current_user_name=current_user_name,new_approve_accounts=new_approve_accounts)     
    
@app.route('/restore_database_request',methods=['POST','GET'])
def restore_database_request():
    uploadedFile = request.files.get('file')
    global connection
    global cursor
    connection.close()
    
    if(uploadedFile.filename.split('.')[1] == 'db'):
        restoring_database = True
        now = datetime.now()
        dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

        originalDbfilePath = ""
        back_up_databases_directory_path = ""
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file == "falcuty_mentor.db":
                    originalDbfilePath = os.path.join(root, file)
                    
        for x in os.walk(os.getcwd()):
            if "back_up_databases" in x[0]:
                back_up_databases_directory_path = x[0]

        shutil.move(originalDbfilePath,os.path.join(back_up_databases_directory_path,"falcuty_mentor"+"_"+dt_string+".db"))
        uploadedFile.save(originalDbfilePath)
        connection = sqlite3.connect(originalDbfilePath)
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()
        restoring_database = False
        return jsonify({'RESULT':'SUCCESS','MSG':'Successfully restored database.'})
    
    elif(uploadedFile.filename.split('.')[1] == 'csv'):
        restoring_database = True
        now = datetime.now()
        dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

        originalDbfilePath = ""
        back_up_databases_directory_path = ""
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file == "falcuty_mentor.db":
                    originalDbfilePath = os.path.join(root, file)
                    
        for x in os.walk(os.getcwd()):
            if "back_up_databases" in x[0]:
                back_up_databases_directory_path = x[0]

        shutil.copyfile(originalDbfilePath,os.path.join(back_up_databases_directory_path,"falcuty_mentor"+"_"+dt_string+".db"))
        
        connection = sqlite3.connect(originalDbfilePath)
        cursor = connection.cursor()
        db_helper.createMentoringTable(cursor)
        db_helper.createStudentTable(cursor)
        db_helper.createProfessorTable(cursor)
        db_helper.createOfflineDataTable(cursor)
        db_helper.createMost_recent_mentoring_updatesTable(cursor)
        CSV_FOLDER =  get_csv_folder_path()
        csv_file = os.path.join(CSV_FOLDER, "csv_file_from_user.csv")
        uploadedFile.save(csv_file)
        df = db_helper.readCsvIntoDataframe(csv_file,originalCVSFile=False)
        connection.execute("PRAGMA foreign_keys = ON;")
        db_helper.insertToStudentTableFromCSVFile(df,cursor)
        db_helper.insertToProfessorTableFromCSVFile(df,cursor)
        db_helper.insertToMentoringTableFromCSVFile(df,cursor,isThereEndDate=True)
        db_helper.insertDataToOffline_dataTable(connection,"DOUBLE_margin_for_max_student_count","0.35")
        connection.commit()    
        restoring_database = False
        return jsonify({'RESULT':'SUCCESS','MSG':'Successfully restored database.'})
    
    else:
        originalDbfilePath = ""
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file == "falcuty_mentor.db":
                    originalDbfilePath = os.path.join(root, file)
        connection = sqlite3.connect(originalDbfilePath)
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()
        return jsonify({'RESULT':'FAIL','MSG':'The file is not type .db nor .csv. Please make sure the right file is selected.'})
    
    return returnMsg
    
@app.before_request
def before_request():
    global new_approve_accounts
    new_approve_accounts = len(User_to_approve.query.all())
    if(restoring_database == True):
        return render_template("maintenance.html")
    else:
        pass

@app.route('/create_account',methods=['POST','GET'])
def create_account():
    return render_template('create_account.html')

@app.route('/create_account_request',methods=['POST','GET'])
def create_account_request():
    try:
        username = request.form['username'].lstrip().rstrip().lower()
        
        active_user_array = User.query.all()
        for user in active_user_array:
            if user.username == username:
                print("username[" + username + "] repeated")
                return jsonify({'RESULT':'FAIL','MSG':"username existed, please choose another username."})
            
        password = request.form['password']
        email = request.form['email'].lstrip().rstrip().lower()
        applyDate = datetime.now()
        applyDateString = applyDate.strftime("%m/%d/%Y %H:%M:%S")
        hashed_password = generate_password_hash(password,method='sha256')
        new_user_to_approve = User_to_approve(username=username,password=hashed_password,email=email,applyDate=applyDateString)
        db.session.add(new_user_to_approve)
        db.session.commit()
        return jsonify({'RESULT':'SUCCESS','MSG':'/login'})
    except sqlalchemy.exc.IntegrityError:
        print("username[" + username + "] repeated")
        return jsonify({'RESULT':'FAIL','MSG':"username existed, please choose another username."})
    except Exception as e:
        print(str(e))
        return jsonify({'RESULT':'FAIL','MSG':str(e)})

@app.route('/approve_accounts',methods=['POST','GET'])
def approve_accounts():
    current_user_name  = ""
    if(current_user.is_authenticated == True):
        current_user_name = current_user.username  
        
    user_approve_array = User_to_approve.query.all()
    approve_account_2d_array = []
    for i in user_approve_array:
        approve_account_inner_array = []
        approve_account_inner_array.append(i.id)
        approve_account_inner_array.append(i.username)
        approve_account_inner_array.append(i.email)
        approve_account_inner_array.append(i.applyDate)
        approve_account_2d_array.append(approve_account_inner_array)
    approve_account_2d_array.reverse()
    
    return render_template("approve_accounts.html",current_user_name=current_user_name,approve_account_2d_array=approve_account_2d_array)

@app.route('/approve_account_request',methods=['POST','GET'])
def approve_account_request():
    try:
        approve_account_id = request.form['approve_account_id']
        approved_account = User_to_approve.query.filter_by(id=approve_account_id).first()
        signup(approved_account.username,approved_account.password)
        User_to_approve.query.filter_by(id=approve_account_id).delete()
        db.session.commit()
        return jsonify({'RESULT':'SUCCESS','MSG':'Account Approved'})
    except Exception as e:
        return jsonify({'RESULT':'FAIL','MSG':str(e)})
    
@app.route('/disapprove_account_request',methods=['POST','GET'])
def disapprove_account_request():
    try:
        approve_account_id = request.form['approve_account_id']
        User_to_approve.query.filter_by(id=approve_account_id).delete()
        db.session.commit()
        return jsonify({'RESULT':'SUCCESS','MSG':'Account Disapproved'})
    except Exception as e:
        return jsonify({'RESULT':'FAIL','MSG':str(e)})    

    
# Running the app here
if __name__ == '__main__':
    FOLDER_PATH = get_current_database_folder_path()     
    falcuty_mentor_db_file = os.path.join(FOLDER_PATH, 'falcuty_mentor.db')  
    connection = sqlite3.connect(falcuty_mentor_db_file)
    connection.execute("PRAGMA foreign_keys = ON;")
    cursor = connection.cursor()
    globalMentoring = db_helper.Mentoring()
    restoring_database = False
    new_approve_accounts = 0
    run_simple('localhost', 5000, app,use_debugger=True, use_evalex=True)