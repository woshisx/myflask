from flask import Flask,render_template,url_for,request,redirect,Blueprint,session,flash
from pymongo import MongoClient
import datetime,os,re,json,random
from fuzzywuzzy import fuzz,process
from flask_login import LoginManager,UserMixin,login_required,current_user,login_user,logout_user
app = Flask(__name__)
conn = MongoClient('localhost', 27017)
db = conn.youtube_db
#user-------------
app.secret_key = 'ds8cix1'
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message_category = "info"
login_manager.login_message = u"请登录！"
login_manager.init_app(app=app)
auth = Blueprint('auth',__name__)