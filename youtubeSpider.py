# -*- coding: utf-8 -*-
import requests,os,re,time,json,shutil,random,threading
from bs4 import BeautifulSoup
from pytube import YouTube,Playlist
import youtube_dl
from pymongo import MongoClient
from moviepy.editor import *

class youtube_link():
    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        self.db = self.conn.youtube_db
        self.play_type = {'list_mark':'yt-lockup yt-lockup-tile yt-lockup-playlist vve-check clearfix','video_mark':'yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix'}
        self.srt_key = 'a2d09c7d76fced01f8be4b1f4cce8bec'
    def youtube_info(self,id):
        link = 'https://www.youtube.com/watch?v=' + id
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        with ydl:
            try:
                result = ydl.extract_info(link, download=False)
                if 'entries' in result:
                    # Can be a playlist or a list of videos
                    video = result['entries'][0]
                else:
                    # Just a video
                    video = result
            except:
                video = None
                if not self.check_link(id):
                    self.db.black_col.insert({'black_id':id})
                print('extract_info eroor')

        return video

    def srt_content(self,id):
        srt_dic = {'en-auto':'','zh-Hans':''}
        link = []
        dic = json.loads(requests.get('https://api.zhuwei.me/v1/captions/' + id + '?api-key=' + self.srt_key).text)
        if dic['meta']['msg'] == 'OK':
            captions = dic['response']['captions']['available_captions']
            if captions:
                for each in captions:
                    if re.search('en',each['language']) or re.search('zh-Hans',each['language']):
                        link.append(each['caption_content_url'])
            if link:
                for each in link:
                    re_dic = json.loads(requests.get(each + '?api-key=' + self.srt_key).text)
                    if re_dic:
                        try:
                            print('srt limit '+ str(re_dic['meta']['limit_remaining']))
                        except:
                            pass
                        if re_dic['meta']['msg'] == 'OK':
                            srt_dic[str(each.split('/')[-1])] = re_dic['contents']['content']
                        else:
                            srt_dic[str(each.split('/')[-1])] = ''
        return srt_dic

    def get_list(self,link):
        playlist_id = []
        if re.search('list=',link):
            res = requests.get(link)
            soup = BeautifulSoup(res.text)
            item = soup.find('div', class_='playlist-videos-container yt-scrollbar-dark yt-scrollbar').find_all('a')
            for each in item:
                playlist_id.append(each.get('href')[9:20])
        return playlist_id

    def prase(self,playlist_id):#检查playlist_id下载的完整度
        for id in playlist_id:
            if not self.check_link(id):
                json_dic = self.youtube_info(id)
                if json_dic:
                    self.db_insert(json_dic, playlist_id)

    def sec_to_hour(self,sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return("%d:%02d:%02d" % (h, m, s))

    def db_insert(self,json_dic,playlist_id):
        insert_dic = {}
        insert_dic['video_id'] = json_dic['id']
        insert_dic['thumbnail'] = json_dic['thumbnail']
        insert_dic['tags'] = json_dic['tags']
        if self.keyword:
            insert_dic['tags'].append(self.keyword)
            insert_dic['keyword'] = self.keyword
        insert_dic['categories'] = json_dic['categories']
        insert_dic['upload_date'] = json_dic['upload_date']
        insert_dic['creator'] = json_dic['creator']
        insert_dic['uploader'] = json_dic['uploader']
        insert_dic['title'] = json_dic['title']
        temp_dic = {}
        temp_dic['sec'] = json_dic['duration']
        temp_dic['hour'] = self.sec_to_hour(int(json_dic['duration']))
        insert_dic['duration'] = temp_dic
        insert_dic['view_count'] = json_dic['view_count']
        insert_dic['like_count'] = json_dic['like_count']
        insert_dic['dislike_count'] = json_dic['dislike_count']
        insert_dic['description'] = json_dic['description']
        temp_dic = {}
        try:
            temp_srt = self.srt_content(json_dic['id'])
            for lan in temp_srt:
                f = open('./static/srt/' + json_dic['id'] + '_' + lan + '.srt', 'w', encoding='utf-8')
                f.write(temp_srt[lan])
                f.close()
                temp_dic[lan] = 'srt/' + json_dic['id'] + '_' + lan + '.srt'
        except:
            temp_dic['zh-Hans'] = ''
        insert_dic['subtitle'] = temp_dic
        insert_dic['video_url'] = 'https://www.youtube.com/watch?v=' + json_dic['id']
        insert_dic['playlist'] = playlist_id
        insert_dic['random'] = random.randint(0,100)
        self.db.col.insert(insert_dic)
        print('---->insert '+ json_dic['id'] +' success<----')
    def search(self,keyword,list = False):
        self.keyword = keyword
        if list :
            res = requests.get('https://www.youtube.com/results?search_query='+ self.keyword)
        else:
            res = requests.get('https://www.youtube.com/results?search_query=' + self.keyword +'&sp=EgIQAw%253D%253D')
        soup = BeautifulSoup(res.text)
        one_video = soup.find_all('div', class_=self.play_type['video_mark'])
        video_list = soup.find_all('div', class_=self.play_type['list_mark'])
        for each in one_video:
            playlist_id = []
            playlist_id.append(each.find('a').get('href')[9:20])
            self.prase(playlist_id)
        for each in video_list:
            playlist_id = self.get_list('https://www.youtube.com'+ each.find('a').get('href'))
            self.prase(playlist_id)

    def get_href(self,keword=None,link=None):
        self.keyword = keword
        res = requests.get(link)
        soup = BeautifulSoup(res.text)
        link_list = soup.findAll(name='a',attrs={"href":re.compile(r'^/watch')})
        for each in link_list:
            playlist_id = []
            playlist_id.append(each.get('href')[9:20])
            self.prase(playlist_id)

    def load_list(self,keyword,link):
        self.keyword = keyword
        self.prase(self.get_list(link))

    def check_link(self,id):
        if self.db.black_col.find({'video_id': id}).count() or self.db.col.find({'video_id':id}).count():
            return True

    def down_load(self,playlist = False,img = False,video = False,keyword = False):
        video_down_list = []
        if playlist:
            self.update_playlist()
        for item in self.db.col.find():
            if keyword:
                if not item['keyword']:
                    self.db.col.update({'_id': item['_id']},{'$set': {'keyword': item['tags'][0]}})
            if video:
                if re.search('www.youtube.com',item['video_url']):
                    temp_list = [item['video_url'],item['video_id']]
                    video_down_list.append(temp_list)
                    temp_list =[]

            if img:
                if re.search('ytimg',item['thumbnail']):
                    print('Downloading ' + item['video_id'] + '.....')
                    f = open('./static/images/%s.jpg'%item['video_id'] , 'ab')
                    f.write(requests.get(item['thumbnail']).content)
                    f.close()
                    self.db.col.update({'_id': item['_id']}, {'$set': {'thumbnail': 'http://my-mixwheel.oss-cn-zhangjiakou.aliyuncs.com/images/%s.jpg'%item['video_id']}})
                    print('download ' + item['video_id'] + '.jpg success')
        for x in video_down_list[:3]:
            t = threading.Thread(target=self.thread_video, args=(x[0],x[1]))
            t.start()


    def thread_video(self,video_url,video_id):
        try:
            print('Downloading ' + video_url + '.....')
            yd_ = YouTube(video_url)
            yd_.streams.filter(progressive=True, subtype='mp4').first().download('./static/video/', video_id)
            print('download ' + video_url + ' success')
            self.db.col.update({'video_id': video_id}, {'$set': {'video_url':'http://47.92.219.115/static/oss/video/%s.mp4'%video_id}})
        except:
            print('Downloading ' + video_url + ' failed')
            self.db.col.remove({'video_id': video_id})

    def update_playlist(self):
        for item in self.db.col.find():
            self.prase(item['playlist'])
            self.keyword = None

    def creat_gif(self):
        i=0
        for item in self.db.col.find():
            if not re.search('www.youtube.com', item['video_url']):
                if not os.path.exists("./static/images/%s.gif" % item['video_id']):
                    print(item['video_id'])
                    try:
                        clip = (VideoFileClip('./static/video/%s.mp4'%item['video_id']).subclip(80,82).resize((240,135)))
                        clip.write_gif("./static/images/%s.gif"%item['video_id'])
                    except :
                        print(i)
                        if i>5:
                            exit()
                        i+=1
                        # print(Exception)
                        # shutil.copyfile("./static/images/%s.jpg"%item['video_id'], "./static/images/%s.gif"%item['video_id'])

yt = youtube_link()
# threads = []
# def fun01():
#     yt.search('Pets & Animals')
# def fun02():
#     yt.load_list('音乐 music',link='https://www.youtube.com/watch?v=o5pSCyzUpqM&list=PLvfcJFF9Y5Qj8NGBoQGGniN0TT-mgVaKl')
# def fun03():
#     yt.down_load(video=True)
# threads.append(threading.Thread(target=fun03))
# threads.append(threading.Thread(target=fun02))
# threads.append(threading.Thread(target=fun03))

# print(yt.youtube_info('Wr7nlnRq3tU'))
# yt.search('吉米今夜秀')

# yt.load_list('扶摇',link='https://www.youtube.com/watch?v=UAE2Yjsu4mw&list=PLooD8l3FSd6nIcdcpSCGT0STWCDi4ghBx')
yt.down_load(video = True)

# yt.creat_gif()

# pl = ['D0ia2Xz3kHc','_cSRo9hN3KM','hWz1KINe5sw','qu7umEB2wFY','aglPHJxaaF8']
# yt.keyword='趣闻'
# yt.prase(pl)

# yt.get_href(keword='Will Smith',link='https://www.youtube.com/channel/UCKuHFYu3smtrl2AwwMOXOlg')




