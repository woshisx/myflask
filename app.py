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

class User(UserMixin):
    pass

def query_user(username):
    users = []
    for each in db.user.find({},{'_id':0}):
        users.append(each)
    for user in users:
        if user['username'] == username:
            return user

# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
@login_manager.user_loader
def load_user(username):
    if query_user(username) is not None:
        curr_user = User()
        curr_user.id = username
        return curr_user

@app.route('/test')
def test():
    categorie_info = ['未分类','电影', '动漫', '综艺', '搞笑', '旅行', '音乐', '游戏', '教育', '科学技术', '体育', '预告片', '汽车', '探索发现', '美食']
    dic = {}
    dic['categorie_info'] = categorie_info
    dic = json.dumps(dic)
    return render_template('test.html',dic=dic)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = query_user(username)
        # 验证表单中提交的用户名和密码
        if user is not None and request.form['password'] == user['password']:
            curr_user = User()
            curr_user.id = username
            # 通过Flask-Login的login_user方法登录用户
            login_user(curr_user,remember=True)
            # 如果请求中有next参数，则重定向到其指定的地址，
            # 没有next参数，则重定向到"index"视图
            next = request.args.get('next')
            return redirect(next or url_for('index'))
        flash('用户名或密码错误 !')
    # GET 请求
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form:
            user_dic = {}
            user_dic['username'] = request.form.to_dict()['username']
            user_dic['password'] = request.form.to_dict()['password']
            user_dic['if_member'] = False
            user_dic['member_end_date'] = None
            user_dic['email'] = None
            user_dic['phone'] = request.form.to_dict()['phone']
            user_dic['upload_file'] = None
            user_dic['user_tag'] = None
            user_dic['review_history'] = None
            db.user.insert(user_dic)
        return redirect(url_for('login'))
    # GET 请求
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/search',methods=['GET','POST'])
def search():
    dic = {}
    if request.method == 'POST':
        if request.form.to_dict():
            keyword = request.form.to_dict()['search']
            choices = []
            main_info = []
            temp = []
            for each in db.col.find():
                choices.append(each['title'])
            relate = process.extract(keyword, choices, limit=60, scorer=fuzz.partial_token_set_ratio)
            [temp.append(i) for i in relate if not i in temp]
            for each in temp:
                main_info.append(db.col.find_one({'title': each}, {'_id': 0}))

            dic['main_info'] = main_info
            dic = json.dumps(dic)
    return render_template('search.html',dic = dic)


@app.route('/watch',methods=['GET','POST'])
def video():
    username = current_user.get_id()
    user_info = {'login':'false'}
    if username is not None:
        user_info = query_user(username)
        user_info.pop('password')
        user_info['login'] = 'true'
    id = request.args.get('id')
    main_info = db.col.find_one({'video_id':id},{'_id': 0 })
    playlist_info = []
    temp_list = []
    relate_info = []
    ad_info = []
    if main_info:
        for each in main_info['playlist']:
            temp = db.col.find_one({'video_id': each},{'_id': 0 })
            if temp:
                playlist_info.append(temp)
        relate = db.col.find({'categories':main_info['categories']},{'_id': 0})
        for each in relate:
            temp_list.append(each)
        if len(temp_list)>10:
            relate_info = random.sample(temp_list, 10)
        else:
            relate_info = temp_list
        for each in db.ads.find({},{'_id': 0 }):
            ad_info.append(each)
        ad_info = random.sample(ad_info,1)[0]
    vi_dic = {}
    vi_dic['main_info'] = main_info
    vi_dic['playlist_info'] = playlist_info
    vi_dic['relate_info'] = relate_info
    vi_dic['ad_info'] = ad_info
    user_info = json.dumps(user_info)
    return render_template('video_main.html',vi_dic = vi_dic,user_info =user_info)

@app.route('/',methods=['GET','POST'])
def index():
    dic = {}
    main_list = []
    temp_list = []
    temp_categories = ['人文地理','深度学习','电影','动漫','综艺','搞笑','旅行','音乐','游戏','教育','科学技术','体育','预告片','汽车','探索发现','美食','编程','云计算 人工智能']
    temp_categories = random.sample(temp_categories,len(temp_categories))
    # temp_categories = []
    # for each in db.col.find():
    #     if each['categories'] not in temp_categories:
    #         temp_categories.append(each['categories'])
    # print(temp_categories)
    for item in temp_categories:
        for each in db.col.find({'categories': item}, {'_id': 0,'categories':1,'video_id':1,'title':1,'duration':1,'view_count':1,'upload_date':1,'creator':1,'thumbnail':1}):
            temp_list.append(each)
        if len(temp_list) > 10:
            temp_list = random.sample(temp_list, len(temp_list))
            main_list.append(temp_list)
        # else:
        #     main_list.append(temp_list)
        temp_list = []
    dic['main_list'] = main_list
    dic = json.dumps(dic)
    return render_template('index.html',title='欢迎来到MixWheel',dic = dic)

@app.route('/register',methods=['GET','POST'])
def signup():
    return render_template('register.html')

@app.route('/userValidate',methods=['GET','POST'])
def userValidate():
    username = request.args.get('username')
    if db.user.find({'username':username}).count():
        return '该用户名已被注册!'
    else:
        return ''

@app.route('/admin/ad',methods=['GET','POST'])
@login_required
def ad():
    if current_user.get_id() == 'admin':
        dic = []
        for each in db.ads.find({},{'_id': 0 }):
            dic.append(each)
        return render_template('admin_ads.html',dic=dic)
    else:
        return 'bye-bye'

@app.route('/admin/ad_post',methods=['POST'])
@login_required
def ad_action():

    if current_user.get_id() == 'admin':
        action = request.args.get('action')
        dic = request.form.to_dict()
        if action == 'insert':
            try:
                if not db.ads.find({'ad_id':dic['ad_id']}).count() and dic['ad_id']:
                    db.ads.insert(dic)
                    return '插入成功'
                else:
                    return '记录已经存在或数据不规范'
            except:
                return '插入出错'
        if action == 'delete':
            try:
                if dic:
                    db.ads.remove({'ad_id':dic['ad_id']})
                    return '删除成功'
            except:
                return '删除出错'
    else:
        return 'bye-bye'

@app.route('/admin/video_post',methods=['GET','POST'])
@login_required
def video_action():
    if current_user.get_id() == 'admin':
        action = request.args.get('action')
        if action =='delete':
            id = request.form.to_dict()['video_id']
            try:
                os.remove('./myflask/static/oss/images/%s.jpg'%id)
            except:
                pass
            try:
                os.remove('E:/oss/images/%s.jpg'%id)
            except:
                pass
            try:
                os.remove('E:/oss/video/%s.mp4'%id)
            except:
                pass
            try:
                os.remove('./myflask/static/oss/video/%s.mp4'%id)
            except:
                pass
            db.col.remove({'video_id': id})
            return id+' deleted'
        if action == 'recategorie':
            info = request.form.to_dict()
            print(info)
            db.col.update({'video_id': info['id']}, {'$set': {'categories': info['categorie']}})
            return info['id'] +' 分类修改为 '+ info['categorie']
    else:
        return 'bye-bye'

@app.route('/admin/video',methods=['GET','POST'])
@login_required
def admin_video():
    if current_user.get_id() == 'admin':
        main_info = []
        categorie_info = ['未分类','人文地理','深度学习','电影','动漫','综艺','搞笑','旅行','音乐','游戏','教育','科学技术','体育','预告片','汽车','探索发现','美食','编程','云计算 人工智能']
        dic = {}
        for each in db.col.find({},{'_id': 0 })[900:]:

            
            main_info.append(each)
        dic['main_info'] = main_info
        dic['categorie_info'] = categorie_info
        dic = json.dumps(dic)
        return render_template('admin_video.html', dic=dic)
    else:
        return 'bye-bye'

def user_mail_confir(address):
    # 导入python里面的这个stmplib这个库
    import smtplib
    # 导入邮件文本模块
    from email.mime.text import MIMEText

    # 设置SMTP服务器
    SMTPServer = "smtp.qq.com"
    # 设置发邮件的地址,也就是自己的邮箱地址.
    sender = "nj17****8@163.com"
    # 邮箱的密码,注意这是你自己的密码哦
    passwd = "lalalala**"

    # 设置发送的内容
    message = "今晚上山打老虎!"
    # 转换为邮件文本,也就是用我们导入的模块email.mime.text的MIMEText方法进行转换
    msg = MIMEText(message)
    # 设置邮件标题
    msg["Subject"] = "来自帅哥的问候"
    # 设置发送者的名称
    msg["From"] = sender
    # 设置好一切基本条件以后,万事俱备了,开始进行连接了.
    # 创建STMP服务器 ,连接STMP的服务器
    mailServer = smtplib.SMTP(SMTPServer, 25)  # 25是邮件专用的端口哦.
    # 登录邮箱
    mailServer.login(sender, passwd)
    # 发送邮件
    mailServer.sendmail(sender, ["957**8@qq.com", "4449***454@qq.com", "nj17449***8@163.com"], msg.as_string())
    # 发送完毕以后,记得退出,怎么样,是不是很简单呢?
    mailServer.quit()


if __name__ == '__main__':
    app.run(debug=True)

