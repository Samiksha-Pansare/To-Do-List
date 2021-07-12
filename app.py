from flask import *
from flask_sqlalchemy import SQLAlchemy
import os
import random
from datetime import datetime
from flask_bootstrap import Bootstrap 
from flask_mail import Mail, Message
import smtplib

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = """PostGreSql link of heroku"""
app.config.update(
    DEBUG=False,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = """Email-ID""" ,
	MAIL_PASSWORD = """"Email-Password"""


)
app.secret_key = "user_new_program"
db = SQLAlchemy(app)
mail = Mail(app)

class login(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(200),nullable = False)
    email_id = db.Column(db.String(200),nullable = False)
    password = db.Column(db.String(200),nullable = False)

    def __repr__(self):
        return '<Email %r>'% self.id

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    content = db.Column(db.String(200),nullable = False)
    completed = db.Column(db.Integer,default = 0)
    date_created = db.Column(db.DateTime,default = datetime.utcnow)
    user_id = db.Column(db.Integer,nullable = False)

    def __repr__(self):
        return '<Task %r>' % self.id

#TODO
"""
    add error msg in register,login
"""
@app.route('/',methods=['POST','GET'])
def register():
    if request.method =='POST':
        new_username = request.form['username']
        email = request.form['email']
        new_password = request.form['password']
        #new_contact = login(username = new_username,email_id = email,password = new_password)
        r = login.query.filter_by(email_id = email).first()
        if r == None:
            try:
                otp = random.randint(100000,999999)
                # otp = 123456
                try:
                    msg = Message("Send Mail Tutorial!",sender="rajeevdemoprojects@gmail.com",recipients= [email])
                    msg.body = "Hello {}" .format(new_username)
                    msg.html = '<h1 style="color:black">Your Verification Code is {}</h1><h3>If you are not logging in To Do manager ,please ignore the message.Do not Share Your code and Password with anyone ,it may result in loss of your personal details</h3>'.format(otp)     
                    mail.send(msg)
                except Exception as e:
                    print(e)
                #db.session.add(new_contact)
                #db.session.commit()
                # check =  login.query.filter_by(email_id = email).first()
                # session['USERNAME'] = check.id
                print(otp)
                session['OTP'] = otp
                session['E'] = email
                session['SECRETMSG'] = new_password
                session['USER'] = new_username
                return render_template('verify.html')
            except:
                return 'error in registering '

        elif r.id >=1 :
            flash("Email Available!!")
            return render_template('register.html')
        else :
            return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/verify',methods=['POST','GET'])
def verify():
    if request.method == 'POST' :
        if "OTP" in session:
            send_code = session['OTP']
            code = request.form['password']
            if send_code == send_code:
                new_username = session['USER']
                email = session['E']
                new_password = session['SECRETMSG']
                new_contact = login(username = new_username,email_id = email,password = new_password)
                db.session.add(new_contact)
                db.session.commit()
                check =  login.query.filter_by(email_id = email).first()
                session['USERNAME'] = check.id
                return render_template('index.html')
            else :
                return 'CODE incorrect'
        else:
            return render_template('register.html')
    else:
        if "OTP" in session:
            return render_template('verify.html')
        else:
            return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def user_login():
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        check =  login.query.filter_by(email_id = email).first()
        if check == None:
            flash("Email Not available")
            return render_template('login.html')
        else:
            if check.password == password :
                name = str(check.username)
                session["USERNAME"] = check.id
                return redirect('/tasks')
            else :
                flash('Password incorrect')
                return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout',methods=['POST','GET'])
def user_logout():
    if "USERNAME" in session:
        session.pop("USERNAME",None)
        flash("Logged out")
        return render_template('login.html')
    else:
        flash("Log In first")
        return render_template('login.html')

##################################  NO UPDATES NEEDED #########################3

@app.route('/tasks',methods=['POST','GET'])
def index ():
    if request.method =='POST':
        task_content = request.form['content']
        if "USERNAME" in session:
            s = session['USERNAME'] 
            new_task = Todo(content = task_content,user_id = s)
        else:
            return redirect('/login')

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/tasks')
        except:
            return 'Issue in script'
    else :
        if "USERNAME" in session:
            s = session['USERNAME'] 
            tasks = Todo.query.filter_by(user_id = s).all()
            # if tasks ==None:
            #     tasks['id'] = 1
            #     tasks ['content'] = 'Demo event for all'
            #     tasks ['data_created'] = datetime.utcnow
            #     tasks['user_id'] = s
            return render_template('index.html',tasks = tasks)
        else :
            return redirect('/login')
@app.route('/delete/<int:id>')
def delete(id):
    if "USERNAME" in session:
        s = session['USERNAME'] 
        task_delete = Todo.query.get_or_404(id)
    else:
        return redirect('/login')

    try:
        db.session.delete(task_delete)
        db.session.commit()
        return redirect('/tasks')
    except:
        return "Problem deleting task"

@app.route('/update/<int:id>',methods=['POST','GET'])
def update(id):
    if "USERNAME" in session:
        s = session['USERNAME'] 
        task = Todo.query.get_or_404(id)
        if request.method =='POST':
            task.content = request.form['content']

            try:
                db.session.commit()
                return redirect('/tasks')
            except:
                return "Error while updating"

        else:

            return render_template('update.html',task = task)
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

