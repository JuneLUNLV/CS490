import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl

class Saved_data:
	def __init__(self):
		self.fromEmail = ""
		self.toEmail = ""
		self.ccEmails = ""
		self.globalServer = ""
		self.globalMsg = ""
		self.globalRcpt = ""

saved_data_object = Saved_data()
	
def login(emailUserName="johnsnow20173@gmail.com",emailPassword="a474561939",port=587,smtp_server="smtp.gmail.com"):
	context = ssl.create_default_context()
	server = smtplib.SMTP(smtp_server, port)
	server.ehlo()  # Can be omitted
	server.starttls(context=context)
	server.ehlo()  # Can be omitted
	server.login(emailUserName, emailPassword)
	saved_data_object.fromEmail = emailUserName;
	saved_data_object.globalServer = server;
	
def setRecipients(receiptEmail,cc=""):
	saved_data_object.toEmail = receiptEmail
	saved_data_object.ccEmails = cc
	

def setEmailSubjectAndContent(subject,content):
	saved_data_object.globalRcpt = saved_data_object.ccEmails.split(",")  + [saved_data_object.toEmail]
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['To'] = saved_data_object.toEmail
	msg['Cc'] = saved_data_object.ccEmails
	my_msg_body = MIMEText(content)
	msg.attach(my_msg_body)
	saved_data_object.globalMsg = msg
	
def sendMail():
	saved_data_object.globalServer.sendmail(saved_data_object.fromEmail, saved_data_object.globalRcpt, saved_data_object.globalMsg.as_string())