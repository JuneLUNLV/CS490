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
from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "cs.sys.testing@gmail.com"
app.config['MAIL_PASSWORD'] =  "a474561939"
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

@app.route("/")
def index():
    mentor_name = "Dr. Yfantis"
    mentor_email = " evangelos.yfantis@unlv.edu"
    
    subject = "Mentor request"
    sender = "jcs.sys.testing@gmail.com"
    recipients = ["ykuovobdrvniuhjmyf@awdrt.org"]
    cc  = []
    body = "Hi,\nYour faculty mentor is " + mentor_name + ".  Please email him at"  + mentor_email + " to schedule an appointment.  Please note, before we can sign the advanced standing form, you will need to have completed your grad plan.  Thanks.\n\n-sys1"
    msg = Message(subject=subject,sender=sender,recipients=recipients,body=body)
    mail.send(msg)
    return render_template("login.html")

run_simple('localhost', 5000, app, use_debugger=True, use_evalex=True)