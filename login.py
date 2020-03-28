from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, fresh_login_required
from urllib.parse import urlparse, urljoin
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\Administrator\\Desktop\\CS490\\login.db"
app.config['SECRET_KEY'] = 'thissecret'
#app.config['USE_SESSION_FOR_NEXT'] = True

#THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#db_file = os.path.join(THIS_FOLDER, 'login.db')   
#db_file = "sqlite:///" + db_file
#print(db_file.replace('\\','\\\\'))


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
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# @app.route('/')
# def index():
#     user = User.query.filter_by(username="anthony").first()
#     if(user == None):
#         return "No such user!"
#     login_user(user)
#     return 'You are now log in!'

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/login')
def login():
    #print (request.args.get('next'))
    session['next'] = request.args.get('next', "/home" )
    #session['next'] = request.args.get('next')
    return render_template('login.html')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url,target))
    return test_url.scheme in ('http','https') and \
        ref_url.netloc == test_url.netloc

@app.route('/login_request',methods=['POST'])
def login_request():
    username = request.form['username']
    form_password = request.form['password']
    #print(username)
    
    user = User.query.filter_by(username=username).first()
    if not user:
        #return jsonify({'RESULT':'User not found'})
        return "<h1>User not found!</h1>"
    
    if check_password_hash(user.password, form_password):
        login_user(user,remember=True)
    
    print('next' in session)
    if 'next' in session:
        next = session['next']
        
        if is_safe_url(next):
            return redirect(next)
    
    #return jsonify({'RESULT':'You are now logged in!'})
    return "<h1>You are logged in!</h1>"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'You are now logged out!'

@app.route('/home')
@login_required
def home():
    return 'The current user is ' + current_user.username

@app.route('/fresh')
@fresh_login_required
def fresh():
    return '<h1>You need to re-log in</h1>'


#@app.route('/signup', methods['GET','POST'])
def signup(username,password):
    #username = request.form['username']
    #password = request.form['password']
    hashed_password = generate_password_hash(password,method='sha256')
    new_user = User(username=username,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

app.run(debug=True)