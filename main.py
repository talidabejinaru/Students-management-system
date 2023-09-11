from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import null
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='kusumachandashwini'

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/students'
db=SQLAlchemy(app)

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))
    rollno=db.Column(db.String(50))

class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sname=db.Column(db.String(50))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))
    groupname=db.Column(db.String(50))

class Secretary(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sname=db.Column(db.String(50))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))

class Series(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    
class Group(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    gname=db.Column(db.String(50))
    seriesname=db.Column(db.String(50))

class Grade(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    value=db.Column(db.String(50))
    subject=db.Column(db.String(50))
    studentname=db.Column(db.String(50))

@app.route('/')
def firstPage():
    return render_template('firstpage.html')

@app.route('/administrator')
def administrator(): 
    return render_template('administrator.html')

@app.route('/student')
def student(): 
    return render_template('student.html')

@app.route('/secretary')
def secretary(): 
    return render_template('secretary.html')

@app.route('/studentinfo')
def studentinfo():
    query = db.engine.execute(f"SELECT g.id, g.value, g.subject, g.studentname FROM `grade` g WHERE g.studentname = '{loggedUserName}'")
    return render_template('studentinfo.html', query=query)

@app.route('/<string:name>') #students details # groups details # grades details 
def details(name):
    if (loggedUserRoll == 'admin'):
        # daca vrem sa mergem in detalii student cu filtru de nume grupa
        if (len(name) == 5):
            query=db.engine.execute(f"SELECT DISTINCT s.id, s.sname, s.email, s.groupname, s.password FROM `student` s WHERE s.groupname = '{name}'") 
            return render_template('studentdetails.html',query=query)

        # daca vrem sa mergem in detalii grupa cu filtru de nume serie
        elif (len(name) == 2):
            query=db.engine.execute(f"SELECT DISTINCT g.id, g.gname, g.seriesname FROM `group` g, `series` s WHERE g.seriesname = '{name}'")
            return render_template('groupsdetails.html',query=query)

        # daca vrem sa mergem in detalii catalog cu filtru de nume student
        else:
            query=db.engine.execute(f"SELECT DISTINCT g.id, g.value, g.subject, g.studentname FROM `grade` g WHERE g.studentname = '{name}'")
            return render_template('gradedetails.html',query=query)

    elif (loggedUserRoll == 'secretary'):
        # daca vrem sa mergem in detalii student cu filtru de nume grupa
        if (len(name) == 5):
            query=db.engine.execute(f"SELECT DISTINCT s.id, s.sname, s.email, s.groupname, s.password FROM `student` s WHERE s.groupname = '{name}'") 
            return render_template('sstudentdetails.html',query=query)

        # daca vrem sa mergem in detalii grupa cu filtru de nume serie
        elif (len(name) == 2):
            query=db.engine.execute(f"SELECT DISTINCT g.id, g.gname, g.seriesname FROM `group` g, `series` s WHERE g.seriesname = '{name}'")
            return render_template('sgroupsdetails.html',query=query)

        # daca vrem sa mergem in detalii catalog cu filtru de nume student
        else:
            query=db.engine.execute(f"SELECT DISTINCT g.id, g.value, g.subject, g.studentname FROM `grade` g WHERE g.studentname = '{name}'")
            return render_template('sgradedetails.html',query=query)

@app.route('/seriesdetails')
def seriesdetails():
    query=db.engine.execute(f"SELECT * FROM `series`") 
    if (loggedUserRoll == 'admin'):
        return render_template('seriesdetails.html',query=query)
    elif (loggedUserRoll == 'secretary'):
        return render_template('sseriesdetails.html',query=query)

@app.route('/secretariesdetails')
def secretariesdetails():
    query=db.engine.execute(f"SELECT * FROM `secretary`") 
    return render_template('secretariesdetails.html',query=query)

@app.route("/deletestudent/<string:id>",methods=['POST','GET'])
@login_required
def deletestudent(id):
    student=Student.query.filter_by(id=id).first()
    studentn=student.sname
    user=User.query.filter_by(username=student.sname).first()
    usern=user.username
    db.engine.execute(f"DELETE FROM `grade` WHERE `grade`.`studentname`='{studentn}'")
    db.engine.execute(f"DELETE FROM `student` WHERE `student`.`id`={id}")
    db.engine.execute(f"DELETE FROM `user` WHERE `user`.`username`='{usern}'")
    flash("Slot Deleted Successful","danger")
    return redirect('/' + student.groupname)

@app.route("/deletesecretary/<string:id>",methods=['POST','GET'])
@login_required
def deletesecretary(id):
    secretary=Secretary.query.filter_by(id=id).first()
    db.engine.execute(f"DELETE FROM `secretary` WHERE `secretary`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/secretariesdetails')

@app.route("/deleteseries/<string:id>",methods=['POST','GET'])
@login_required
def deleteseries(id):
    series=Series.query.filter_by(id=id).first()
    seriesname=series.name
    db.engine.execute(f"DELETE FROM `group` WHERE `group`.`seriesname`='{seriesname}'")
    db.engine.execute(f"DELETE FROM `series` WHERE `series`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    if (loggedUserRoll == 'admin'):
        return redirect('/seriesdetails')
    elif (loggedUserRoll == 'secretary'):
        return redirect('/sseriesdetails')

@app.route("/deletegroup/<string:id>",methods=['POST','GET'])
@login_required
def deletegroup(id):
    group=Group.query.filter_by(id=id).first()
    db.engine.execute(f"DELETE FROM `group` WHERE `group`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/'+ group.seriesname)

@app.route("/deletegrade/<string:id>",methods=['POST','GET'])
@login_required
def deletegrade(id):
    grade=Grade.query.filter_by(id=id).first()
    db.engine.execute(f"DELETE FROM `grade` WHERE `grade`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/'+ grade.studentname)

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        encpassword=generate_password_hash(password)

        if user and check_password_hash(user.password,password):
            global loggedUserName
            loggedUserName = user.username
            global loggedUserRoll
            loggedUserRoll = user.rollno
            login_user(user)
            flash("Login Success","primary")
            if user.rollno == "admin":
                return redirect(url_for('administrator'))
            elif user.rollno == "student":
                return redirect(url_for('student'))
            elif user.rollno == "secretary":
                return redirect(url_for('secretary'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/addstudent',methods=['POST','GET'])
@login_required
def addstudent():
    if request.method=="POST":
        sname=request.form.get('sname')
        email=request.form.get('email')
        password=request.form.get('password')
        groupname=request.form.get('groupname')
        rollno = "student"

        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            if (loggedUserRoll == 'admin'):
                return render_template('/addstudent.html')
            elif (loggedUserRoll == 'secretary'):
                return render_template('/saddstudent.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`, `rollno`) VALUES ('{sname}','{email}','{encpassword}','{rollno}')")
        query=db.engine.execute(f"INSERT INTO `student` (`sname`,`email`,`password`,`groupname`) VALUES ('{sname}','{email}','{encpassword}','{groupname}')")

        flash("Booking Confirmed","info")

    if (loggedUserRoll == 'admin'):
        return render_template('addstudent.html')
    elif (loggedUserRoll == 'secretary'):
        return render_template('saddstudent.html')

@app.route('/addsecretary',methods=['POST','GET'])
@login_required
def addsecretary():
    if request.method=="POST":
        sname=request.form.get('sname')
        email=request.form.get('email')
        password=request.form.get('password')
        rollno = "secretary"

        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            
            return render_template('/addsecretary.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`, `rollno`) VALUES ('{sname}','{email}','{encpassword}','{rollno}')")
        query=db.engine.execute(f"INSERT INTO `secretary` (`sname`,`email`,`password`) VALUES ('{sname}','{email}','{encpassword}')")

        flash("Booking Confirmed","info")

    return render_template('addsecretary.html')

@app.route('/addseries',methods=['POST','GET'])
@login_required
def addseries():
    if request.method=="POST":
        name=request.form.get('name')
        query=db.engine.execute(f"INSERT INTO `series` (`name`) VALUES ('{name}')")
    
        flash("Booking Confirmed","info")
    
    if (loggedUserRoll == 'admin'):
        return render_template('addseries.html')
    elif (loggedUserRoll == 'secretary'):
        return render_template('saddseries.html')

@app.route('/addgroup',methods=['POST','GET'])
@login_required
def addgroup():
    if request.method=="POST":
        gname=request.form.get('gname')
        seriesname=request.form.get('seriesname')
        query=db.engine.execute(f"INSERT INTO `group` (`gname`,`seriesname`) VALUES ('{gname}','{seriesname}')")

        flash("Booking Confirmed","info")

    if (loggedUserRoll == 'admin'):
        return render_template('addgroups.html')
    elif (loggedUserRoll == 'secretary'):
        return render_template('saddgroups.html')

@app.route('/addgrade',methods=['POST','GET'])
@login_required
def addgrade():
    if request.method=="POST":
        value=request.form.get('value')
        subject=request.form.get('subject')
        studentname=request.form.get('studentname')
        query=db.engine.execute(f"INSERT INTO `grade` (`value`,`subject`,`studentname`) VALUES ('{value}','{subject}','{studentname}')")

        flash("Booking Confirmed","info")

    if (loggedUserRoll == 'admin'):
        return render_template('addgrade.html')
    elif (loggedUserRoll == 'secretary'):
        return render_template('saddgrade.html')

app.run(debug=True)    