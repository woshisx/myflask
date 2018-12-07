import oss2
from itertools import islice
from myflask import *
auth = oss2.Auth('LTAI9KoPJsTapdyo', '5kgYBIG3kGTLVjNXMdeOdg5xDZUgOi')
bucket = oss2.Bucket(auth, 'oss-cn-zhangjiakou.aliyuncs.com', 'my-mixwheel')

def oss_list():
    file_list = []
    for b in islice(oss2.ObjectIterator(bucket), 50):
        file_list.append(b.key)
    return file_list
def oss_exist(out_path,file_name):
    return bucket.object_exists(out_path+file_name)
def oss_upload(local_path,file_arr,out_path):
    for each in file_arr:
        bucket.put_object_from_file(out_path+each,local_path+each)
def oss_delete(out_path,file_name):
    bucket.delete_object(out_path+file_name)
def list_file(path):
    temp_list = []
    fs = os.listdir(path)
    if fs:
        for obj in fs:
            tmp_path = os.path.join(path, obj)
            if not os.path.isdir(tmp_path):
                temp_list.append(obj)
    return temp_list
def server_check():
    pass
