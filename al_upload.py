import oss2,os,re,shutil
from itertools import islice
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.youtube_db
auth = oss2.Auth('LTAI9KoPJsTapdyo', '5kgYBIG3kGTLVjNXMdeOdg5xDZUgOi')
bucket = oss2.Bucket(auth, 'oss-cn-zhangjiakou.aliyuncs.com', 'my-mixwheel')

def oss_list():
    file_list = []
    for b in islice(oss2.ObjectIterator(bucket), 5000):
        file_list.append(b.key)
    return file_list
def oss_exist(out_path,file_name):
    return bucket.object_exists(out_path+file_name)
def oss_upload(local_path,out_path):
    for each in list_file(local_path):
        if not oss_exist(out_path,each):
            # bucket.put_object_from_file(out_path+each,local_path+each)
            # shutil.copy('E:/oss/video/'+each,'E:/oss/upload/'+each)
            db.col.remove({'video_id': each.split('.')[0]})
            print(each)
def oss_delete(file):
    bucket.delete_object(file)
def list_file(path):
    temp_list = []
    fs = os.listdir(path)
    if fs:
        for obj in fs:
            tmp_path = os.path.join(path, obj)
            if not os.path.isdir(tmp_path):
                temp_list.append(obj)
    return temp_list
def server_clean():
    for each in oss_list():
        if re.search('.mp4',each):
            id = each.split('/')[1].split('.')[0]
            if not db.col.find({'video_id':id}).count():
                oss_delete(each)

# oss_upload('C:/Users/chenxing/PycharmProjects/myweb/myflask/static/oss/images/','images/')

oss_upload('E:/oss/video/', 'video/')
