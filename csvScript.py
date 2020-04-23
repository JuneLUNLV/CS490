import sqlite3
import os
import database_helper as db_helper
import pandas as pd

def get_current_database_folder_path():
  current_database_folder_path = ""
  for x in os.walk(os.getcwd()):
      if "current_database" in x[0]:
          current_database_folder_path = x[0]    
  return current_database_folder_path

def get_csv_folder_path():
  current_database_folder_path = ""
  for x in os.walk(os.getcwd()):
      if "csv_folder" in x[0]:
          current_database_folder_path = x[0]    
  return current_database_folder_path 

def runScript():
  FOLDER_PATH = get_current_database_folder_path()
  falcuty_mentor_db_file = os.path.join(FOLDER_PATH, 'falcuty_mentor.db')   
  connection = sqlite3.connect(falcuty_mentor_db_file)
  cursor = connection.cursor()
  db_helper.createStudentTable(cursor)
  db_helper.createProfessorTable(cursor)
  db_helper.createMentoringTable(cursor)
  db_helper.createOfflineDataTable(cursor)
  db_helper.createMost_recent_mentoring_updatesTable(cursor)

  connection.execute("PRAGMA foreign_keys = ON;")

  CSV_FOLDER_PATH = get_csv_folder_path()
  csv_file = os.path.join(CSV_FOLDER_PATH, 'faculty_mentor_master_list.csv')  
  df = db_helper.readCsvIntoDataframe(csv_file)

  db_helper.insertToStudentTableFromCSVFile(df,cursor)
  db_helper.insertToProfessorTableFromCSVFile(df,cursor)
  db_helper.insertToMentoringTableFromCSVFile(df,cursor)
  db_helper.insertDataToOffline_dataTable(connection,"DOUBLE_margin_for_max_student_count","0.35")

  connection.commit()
  connection.close()
