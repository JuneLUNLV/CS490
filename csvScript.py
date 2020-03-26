import sqlite3
import os
import database_helper as db_helper
import pandas as pd

def runScript():
  connection = sqlite3.connect("falcuty_mentor.db")
  cursor = connection.cursor()
  db_helper.createStudentTable(cursor)
  db_helper.createProfessorTable(cursor)
  db_helper.createMentoringTable(cursor)
  db_helper.createOfflineDataTable(cursor)

  connection.execute("PRAGMA foreign_keys = ON;")

  THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
  csv_file = os.path.join(THIS_FOLDER, 'faculty_mentor_master_list.csv')
  df = db_helper.readCsvIntoDataframe(csv_file)

  db_helper.insertToStudentTableFromCSVFile(df,cursor)
  db_helper.insertToProfessorTableFromCSVFile(df,cursor)
  db_helper.insertToMentoringTableFromCSVFile(df,cursor)
  db_helper.insertDataToOffline_dataTable(connection,"DOUBLE_margin_for_max_student_count","0.35")

  connection.commit()
  connection.close()