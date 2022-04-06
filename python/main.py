from enum import unique
from os import name
from flask import Flask,render_template,request,session,redirect,url_for,flash,Response
from flask.helpers import url_for
from io import BytesIO
from flask.wrappers import Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import query
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import json

with open('config.json','r') as c:
    params = json.load(c)["params"]


#MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='mohammedqurram'

#this is for getting user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# SMTP MAIL SERVER SETTINGS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hospman'
db=SQLAlchemy(app)

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True) 
    firstname=db.Column(db.String(500))
    lastname=db.Column(db.String(500))
    phonenum=db.Column(db.Integer)
    email=db.Column(db.Integer)
    caddress=db.Column(db.String(500))
    paddress=db.Column(db.String(500))
    mil=db.Column(db.Integer,unique=True)
    mcaddress=db.Column(db.String(500))
    password=db.Column(db.String(1000))

class Patients(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True) 
    name=db.Column(db.String(20))
    age=db.Column(db.Integer)
    bmh=db.Column(db.String(1000))
    phonenum=db.Column(db.Integer)
    email=db.Column(db.String(500))
    address=db.Column(db.String(1000))    
    cname=db.Column(db.String(20))
    cphonenum=db.Column(db.Integer)

class Img(UserMixin,db.Model):
    rid=db.Column(db.Integer,primary_key=True) 
    id=db.Column(db.Integer) 
    imgi=db.Column(db.Text)
    name=db.Column(db.Text)
    mimetype=db.Column(db.Text) 


class Healthc(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    health=db.Column(db.String(100))
    date=db.Column(db.String(100))    


    




#here we will pass endpoints and rum the func

@app.route("/")
def hello_world():
    return render_template('index.html') 


@app.route("/addnew", methods=['POST','GET'])
def addnew():

    if request.method == "POST":
        name=request.form.get('name')
        age=request.form.get('age')
        bmh=request.form.get('bmh')
        phonenum=request.form.get('phonenum')
        email=request.form.get('email')
        address=request.form.get('address')
        cname=request.form.get('cname')
        cphonenum=request.form.get('cphonenum')
       
        #new_patient=db.engine.execute(f"INSERT INTO 'patients' ('name','age','bmh','phonenum','email','address','cname','cphonenum') VALUES ('{name}','{age}','{bmh}','{phonenum}','{email}','{address}','{cname}','{cphonenum}')")
        #return render_template('reportbug.html')

        addnewp=Patients(name=name,age=age,bmh=bmh,phonenum=phonenum,email=email,address=address,cname=cname,cphonenum=cphonenum)
        db.session.add(addnewp)
        db.session.commit()
        return redirect('/patients')


    return render_template('addnew.html')
    
       


@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    posts=Patients.query.filter_by(id=id).first()
    if request.method == "POST":
        name=request.form.get('name')
        age=request.form.get('age')
        bmh=request.form.get('bmh')
        phonenum=request.form.get('phonenum')
        email=request.form.get('email')
        address=request.form.get('address')
        cname=request.form.get('cname')
        cphonenum=request.form.get('cphonenum')
        db.engine.execute(f"UPDATE `patients` SET `name` = '{name}', `age` = '{age}', `bmh` = '{bmh}', `phonenum` = '{phonenum}', `email` = '{email}', `address` = '{address}', `cname` = '{cname}', `cphonenum` = '{cphonenum}' WHERE `patients`.`id` = {id};")
        flash("profile updated","success")
        return redirect('/patients')
    
    return render_template('edit.html',posts=posts)

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`id` = '{id}'")
    flash("profile deleted","danger")
    return redirect('/patients')


@app.route("/uploads",methods=['POST','GET'])
def uploads():
    return render_template('upload.html')    



@app.route('/upload', methods=['POST','GET'])
def upload():
    pid=request.form.get('pid')
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(id=pid, imgi=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()
    flash("health report uploaded","success")
    return redirect('/patients')
        

@app.route("/download/<int:rid>", methods=['POST','GET'])
def download(rid):
    #rid=request.args.get('rid',default=0,type=int).first()
    #print(rid)
    img=Img.query.filter_by(rid=rid).first()
    #print(img.name)
    #if not img:
        #return 'Img Not Found!', 404

    return Response(img.imgi, mimetype=img.mimetype)
    #return "img_download"

 
@app.route('/updatehc', methods=['POST'])
def update():    
    if request.method == 'POST':

        pid=request.form.get('pid')

        health=request.form.get('health')
        date=request.form.get('date')
        UpdateHealth=Healthc(pid=pid,health=health,date=date)
        db.session.add(UpdateHealth)
        db.session.commit()
        #return render_template('patients.html')
        flash("health condition updated","success")
        return redirect('/patients')

    return redirect('/healthc')










    
 
  
@app.route("/login",methods=['POST','GET'])
def login():
    

     if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for('patients'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    


     return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


    

@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method == "POST":
        firstname=request.form.get('firstname')
        lastname=request.form.get('lastname')
        phonenum=request.form.get('phonenum')
        email=request.form.get('email')
        caddress=request.form.get('caddress')
        paddress=request.form.get('paddress')
        mil=request.form.get('mil')
        mcaddress=request.form.get('mcaddress')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)
        #new_user=db.engine.execute(f"INSERT INTO 'user' ('firstname','lastname','phonenum','idno','caddress','paddress','mil','mcaddress','password') VALUES ('{firstname}','{lastname}','{phonenum}','{idno}','{caddress}','{paddress}','{mil}','{mcaddress}','{encpassword}')")
        #return render_template('login.html')

        newuser=User(firstname=firstname,lastname=lastname,phonenum=phonenum,email=email,caddress=caddress,paddress=paddress,mil=mil,mcaddress=mcaddress,password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        return render_template('login.html')

 

    

    return render_template('signup.html')
    
@app.route("/reportbug",methods=['POST','GET'])
def reportbug():
     if request.method == "POST":
         email=request.form.get('email')
         prob=request.form.get('prob')
         

         mail.send_message('HOSPITAL MANAGEMENT SYSTEM', sender=params['gmail-user'], recipients=['mdqurramhhh@gmail.com'],body=f"The feedback is :\n{prob} \nfrom:\n{email}")
         flash("Email was sent, thankyou for your feedback","success")


        
         return render_template('reportbug.html')


  
     return render_template('reportbug.html')

@app.route("/patients")
@login_required
def patients():
    em=current_user.email
    query=db.engine.execute(f"SELECT id, name, email, phonenum FROM `patients` WHERE email='{em}'")
    return render_template('patients.html',query=query)    


@app.route("/personal")
def personal():

    
    pid=request.args.get('id',default=0,type=int)

    em=current_user.email
    print(pid)

    query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}' AND id='{pid}'")

 
    
    return render_template('personal.html',query=query)



@app.route("/reports")
def reports():
    id=request.args.get('id',default=0,type=int)
    
    print(id)

    #query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}' AND id='{pid}'")
    query=db.engine.execute(f"SELECT rid, id, name FROM `img` WHERE id='{id}'")

    
 
    
    return render_template('reports.html',query=query)




       
@app.route("/healthc",methods=['POST','GET'])
def healthc():
    pid=request.args.get('id',default=0,type=int)

    #em=current_user.email
    print(pid)

    query=db.engine.execute(f"SELECT date, health FROM `healthc` WHERE pid='{pid}'")

 
    
    #return render_template('personal.html',query=query)

    return render_template('healthc.html',query=query)



@app.route("/profile")
@login_required
def profile():

    pid=request.args.get('id',default=0,type=int)

    em=current_user.email
    print(pid)

    query=db.engine.execute(f"SELECT id, name, email, phonenum FROM `patients` WHERE email='{em}' AND id='{pid}'")

    return render_template('patients.html',query=query)
    

 
app.run(debug=True)    