from flask import Flask,request,render_template,redirect, url_for, request
from flask import *  
from pymongo import MongoClient
import pymongo
from flask_mail import *  
from random import *
import os
import datetime
from datetime import date
import pandas as pd
from redis import Redis
from rq import Queue


def get_database(val):
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = 'mongodb+srv://9retam-mongodb:yy2hWaBD5EWbUfl2@cluster0.pafid.mongodb.net/test'

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[val]

myapp = Flask(__name__)
mail = Mail(myapp) 
myapp.config["MAIL_SERVER"]='smtp.gmail.com'  
myapp.config["MAIL_PORT"] = 465      
myapp.config["MAIL_USERNAME"] = 'rahulr271198@gmail.com'  
myapp.config['MAIL_PASSWORD'] = 'ivruyaxordytzmnh'  
myapp.config['MAIL_USE_TLS'] = False  
myapp.config['MAIL_USE_SSL'] = True  
mail = Mail(myapp)  
otp = randint(000000,999999)

#curr_loc = os.path.dirname(os.path.abspath(__file__))

tskq = Queue(connection=Redis())

def sendmail(q,a,val):
        email =  session['emailid'] 
        msg = Message('Reminder for '+val,sender = 'rahulr271198@gmail.com', recipients = [email])  
        msg.body = 'You have 10 minutes remaining for the task ' + val  
        #mail.send(msg)
        dat = datetime.datetime(int(q[0]), int(q[1]), int(q[2]), a[0], a[1])
        tskq.enqueue_at(dat,mail.send(msg))
'''def sendmail(taskname):
    email =  session['emailid'] 
    msg = Message('Reminder for '+taskname,sender = 'retamroy09@gmail.com', recipients = [email])  
    msg.body = 'You have 10 minutes remaining for the' + taskname  
    mail.send(msg)'''    

@myapp.route('/')
def homepage():
    return render_template('homepage.html')

@myapp.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == "POST":
       emailid = request.form.get("email")
       username = request.form.get("username")
       password = request.form.get("password")
       session['username'] = username 
       session['emailid'] = emailid
       t = emailid.split('.')
       dbname = get_database(t[0]+t[1])
       collection_name = dbname["login"]
       item_details = collection_name.find()
       if(item_details):
            for item in item_details:
                if(item['username']==username and item['password']==password):
                    return redirect('/Loggedin')
                else:
                    return "invalid username/password"
       return "invalid emailid"
    return render_template('login.html')

@myapp.route('/Loggedin', methods=['GET', 'POST'])
def Loggedin():
    return render_template('loggedin.html')

@myapp.route('/SignUp', methods = ['GET','POST'])
def SignUp():
    return render_template('register.html')

@myapp.route('/verify',methods = ["POST"])  
def verify():  
    email = request.form["email"]  
    msg = Message('OTP for registration with watchify',sender = 'rahulr271198@gmail.com', recipients = [email])  
    msg.body = str(otp)  
    mail.send(msg)  
    return render_template('verify.html')

@myapp.route('/validate',methods=["POST"])   
def validate():  
    user_otp = request.form['otp']  
    if otp == int(user_otp):  
        print("<h3> Email  verification is  successful </h3>")
        return redirect('/register')
    return "<h3>failure, OTP does not match</h3>"

@myapp.route('/register', methods =["GET", "POST"])
def register():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       emailid = request.form.get("email")
       username = request.form.get("username")
       password = request.form.get("password") 
       t = emailid.split('.')
       dbname = get_database(t[0]+t[1])
       collection_name = dbname["login"]
       item = {
         "username" : username,
         "password" : password,
         "email" : emailid
        }
       collection_name.insert_one(item)
       return "you have successfully registered"
    return render_template("createid.html")

@myapp.route('/addtask', methods=['GET', 'POST'])
def addtask():
    if request.method == 'POST':
        starttime = request.form.get("st")
        endtime = request.form.get("et")
        taskname = request.form.get("tn")
        reminder = request.form.get("gr")
        today = str(date.today())
        q = today.split('-')
        today = q[2]+'-'+q[1]+'-'+q[0]
        t = session['emailid'].split('.')
        dbname = get_database(t[0]+t[1])
        collection_name = dbname[today]
        item = {
         "date" : today,  
         "starttime" : starttime,
         "endtime" : endtime,
         "taskname" : taskname,
         "reminder" : reminder
        }
        collection_name.insert_one(item)
        if(reminder == 'Y'):
            a = endtime.split(':')
            a[0] = int(a[0])
            a[1] = int(a[1])
            if(a[1]>=10):
                a[1] = a[1]-10
            else:
                a[1] = 60 + a[1]-10
                if a[0]!=0:
                    a[0] = a[1]-1
                else:
                    a[0] = 23
            sendmail(q,a,taskname)
            #tskq.enqueue_at(datetime.datetime(int(q[0]), int(q[1]), int(q[2]), a[0], a[1]),sendmail,taskname)
    return render_template('addtask.html')

@myapp.route('/display', methods=['GET', 'POST'])
def display():
    t = session['emailid'].split('.')
    dbname = get_database(t[0]+t[1])
    today = str(date.today())
    q = today.split('-')
    today = q[2]+'-'+q[1]+'-'+q[0]
    collection_name = dbname[today]
    item_details = collection_name.find()
    dic = {}
    it = 1
    for item in item_details:
        dic['task '+ str(it)] = {}
        for key,values in item.items():
                if(key!='_id'):
                  dic['task '+ str(it)][key] = values 
        it += 1           
    return render_template('display.html', output_data = dic) 

@myapp.route('/previously', methods=['GET', 'POST'])
def previously():
    t = session['emailid'].split('.')
    dbname = get_database(t[0]+t[1])
    w = dbname.list_collection_names()
    dic = {}
    for collection_name in w:
        if collection_name!='login' and collection_name!='feedback':
                item_details = dbname[collection_name].find()
                it = 1
                dic[collection_name] = {}
                for item in item_details:
                    dic[collection_name]['task ' + str(it)] = {}
                    for key,values in item.items():
                            if(key!='_id' and key!='date'):
                                dic[collection_name]['task ' + str(it)][key] = values 
                    it += 1           
    return render_template('previously.html', output_data = dic) 

if __name__ == '__main__':
       myapp.secret_key = 'mysecret'
       myapp.run(debug=True)