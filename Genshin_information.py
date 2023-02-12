#モジュールをインポート
import tweepy
import requests
import datetime as dt
import pytz
import time
import configparser
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os
import discord
import asyncio
import aiohttp
import json
import collections
import interactions

config=configparser.ConfigParser(interpolation=None)
config.read('config.ini')

#ver1.0 正式リリース
#ver1.1 アナウンス機能の追加
#ver1.2 discord に対応
#ver1.3 スラッシュコマンド 1 の実装
#ver1.4.1 ステータスの取得の一部機能の開放(キャラ情報)
#ver1.4.2 ステータスの取得の一部機能の開放(ステータス(聖遺物))
#ver1.5 uidをアカウントに紐づけるコマンドの追加とステータスの取得時に参照を可能に
version="ver1.5"

with open("characterJP.json","r",encoding="utf-8_sig") as f:
    charactersJP=json.load(f)
    f.close()

with open("charactersEN.json","r",encoding="utf-8_sig") as f:
    charactersEN=json.load(f)
    f.close()

with open("uid-list.json","r",encoding="utf-8_sig") as f:
    uid_list=json.load(f)
    f.close()

#Twitter API
API_key = config.get('KEYS','API_key')
API_key_Secret = config.get('KEYS','API_key_Secret')
Access_Token = config.get('KEYS','Access_Token')
Access_Token_Secret = config.get('KEYS','Access_Token_Secret')
Bearer_Token = config.get('KEYS','Bearer_Token')

#LINE Notify
TOKEN = config.get('KEYS','line')
api_url = config.get('KEYS','api_url')

#Discord API
disc_web_url = config.get('KEYS','discord_webhook_url')
discord_token = config.get('KEYS','discord_TOKEN')
channel_id = config.get('KEYS','CHANNEL_ID')
client=discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

#各変数の定義
search_word = 'from:@Genshin_7 -毎日チャレンジ！ -RT -#テイワット放送局'
USER='@Genshin_7'
item_num = 1
user_id = 1070960596357509121
tweet = []
tweet.clear()
tweetcopy = []
tweetcopy.clear()
path = config.get('PATH','path')
pathtxt = config.get('PATH','pathtxt')
tweet_text_file=pathtxt+"\\tweet_text.txt"
tweet_text_now_file=pathtxt+"\\tweet_text_now.txt"
search_url = config.get('KEYS','search_url')
query_params = {'query': '(from:Genshin_7 -ご参加ありがとうございます！ -毎日チャレンジ！ -RT -#テイワット放送局)','expansions': 'attachments.media_keys', 'media.fields': 'url'}
number_of_trials=20
sleep_time=15
item_list = ['3', '4', '5','6','7','8','9','10','11','12','13','14','15']
download_failed=0
status_code_is_not_200=0
network_not_found=0
number_of_executions_count=0
line_num_txt=24
line_num_image=23
line_num_txt=line_num_txt-1
line_num_image=line_num_image-1
sleeptime_min_hour=int(config.get('SETTINGS','sleeptime_min_hour'))
sleeptime_min_minute=int(config.get('SETTINGS','sleeptime_min_minute'))
sleeptime_min_second=int(config.get('SETTINGS','sleeptime_min_second'))
sleeptime_max_hour=int(config.get('SETTINGS','sleeptime_max_hour'))
sleeptime_max_minute=int(config.get('SETTINGS','sleeptime_max_minute'))
sleeptime_max_second=int(config.get('SETTINGS','sleeptime_max_second'))
sleeptime_min=str(sleeptime_min_hour)+":"+str(sleeptime_min_minute)+":"+str(sleeptime_min_second)
sleeptime_max=str(sleeptime_max_hour)+":"+str(sleeptime_max_minute)+":"+str(sleeptime_max_second)
sleep_min=dt.time(sleeptime_min_hour,sleeptime_min_minute,sleeptime_min_second)
sleep_max=dt.time(sleeptime_max_hour,sleeptime_max_minute,sleeptime_max_second)
hour_list=[0]*24
minute_list=[0]*60
second_list=[0]*60
for i in range(24):
    hour_list[i]=i
for i in range(60):
    minute_list[i]=i
    second_list[i]=i
datas_path='..\\config.ini'
now_path=str(os.getcwd())
stop_time_list=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,60,120,180,240,300,1440]

image_urls = []

#twitter API
auth = tweepy.OAuthHandler(API_key, API_key_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)
api = tweepy.API(auth)

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {Bearer_Token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def menu_time():
    t2=time.time()
    stop_time=t2-t1
    if stop_time>=86400:
        day=int(stop_time/60/60/24)
        if (((stop_time/60/60/24)-day)*60*60*24)>=3600:
            hour=int(((((stop_time/60/60/24)-day)*60*60*24)/60/60))
            if (((stop_time/60/60/24)-1)*60*60*24)>=60:
                minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
            else:
                minute=0
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
        else:
            hour=0
            if (((stop_time/60/60/24)-1)*60*60*24)>=60:
                minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
            else:
                minute=0
                second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
    elif stop_time>=3600:
        day=0
        hour=int((stop_time/60/60))
        if (((stop_time/60/60)-hour)*60)>=1:
            minute=int(((((stop_time/60/60)-(hour+(day*24)))*60*60)/60))
            second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
        else:
            minute=0
            second=int((stop_time)-((day*24*60*60)+(hour*60*60)+(minute*60)))
    elif stop_time>=60:
        day=0
        hour=0
        minute=int((stop_time/60))
        second=int(((stop_time/60)-minute)*60)
    elif stop_time<60:
        day=0
        hour=0
        minute=0
        second=int(stop_time)
    time_stop=tk.Toplevel()
    time_stop.geometry("300x30+500+300")
    time_stop.title("経過時間")
    times=tk.Label(time_stop,text=str(day)+"日"+str(hour)+"時間"+str(minute)+"分"+str(second)+"秒", font=("MSゴシック", "15", "bold"))
    times.pack()

def writeToLog(msg):
    numlines=int(log.index('end - 1 line').split('.')[0])
    log['state']='normal'
    #if numlines==24:
    # #log.delete(1.0, 2.0)
    if log.index('end-1c')!='1.0':
        log.insert('end','\n')
    log.insert('end',msg)
    log.see("end")
    log['state']='disabled'

def writeToLog_discord(msg):
    numlines=int(log2.index('end - 1 line').split('.')[0])
    log2['state']='normal'
    #if numlines==24:
    # #log.delete(1.0, 2.0)
    if log2.index('end-1c')!='1.0':
        log2.insert('end','\n')
    log2.insert('end',msg)
    log2.see("end")
    log2['state']='disabled'

def menu_update():
    def show_selected():
        #更新頻度の更新
        global sleep_time
        sleep_time=int(time_combobox.get())
        now_sleep['text']="現在の更新頻度　"+str(sleep_time)+"秒"
        writeToLog("現在の更新頻度を"+now_sleep+"秒に変更しました。")

    sleeptime=tk.Toplevel()
    sleeptime.geometry("250x100+500+300")
    sleeptime.title("SleepTime")
    time_combobox = ttk.Combobox(master=sleeptime,values=item_list,height=5, width=7, justify="center",state="readonly")
    now_sleep = tk.Label(sleeptime,text="現在の更新頻度　"+str(sleep_time)+"秒", font=("MSゴシック", "15", "bold"))
    button = tk.Button(sleeptime,text="decision",command=show_selected)
    time_combobox.pack()
    button.pack()
    now_sleep.pack()
    pass

def txt_file():
    def txt_update():
        global pathtxt,tweet_text_file,tweet_text_now_file,config
        pathtxts=textBox2.get()
        pathtxts=str(pathtxts)
        pathtxts='pathtxt=r"'+pathtxts+'"'
        with open(datas_path,mode="r") as files:
            file_lists=files.read().split("\n")
            files.close()
        file_lists[line_num_txt] = pathtxts
        len_file=len(file_lists)
        for i in range(len_file):
            if i==0:
                tmp=str(file_lists[i])
            else:
                tmp=str(tmp)+str("\n")+str(file_lists[i])
        file_lists=tmp
        with open(datas_path, mode="w") as files:
            files.writelines(file_lists)
            files.close()
        config.read('..\\config.ini')
        pathtxt = config.get('PATH','pathtxt')
        tweet_text_file=pathtxt+"\\"+'tweet_text.txt'
        tweet_text_now_file=pathtxt+"\\"+'tweet_text_now.txt'
        temp=("txtファイルの保存先を”"+str(config.get('PATH','pathtxt'))+"”に変更しました。")
        writeToLog(temp)
    txt=tk.Toplevel()
    txt.geometry("705x75+500+300")
    txt.title("txtの保存先変更")
    txt_label=tk.Label(txt,text="ファイルパスを絶対パスで設定(\\\\で区切る))", font=("MSゴシック", "13"))
    textBox2=tk.Entry(txt,width=117)
    textBox2.place(x=0,y=20)
    button=tk.Button(txt,text='決定',command=txt_update)
    button.place(x=670,y=50)
    txt_label.pack()

def image_file():
    def image_update():
        global path,config
        paths=textBox3.get()
        paths=str(paths)
        paths='path=r"'+paths+'"'
        with open(datas_path,mode="r") as files:
            file_lists=files.read().split("\n")
            files.close()
        file_lists[line_num_image] = paths
        len_file=len(file_lists)
        for i in range(len_file):
            if i==0:
                tmp=str(file_lists[i])
            else:
                tmp=str(tmp)+str("\n")+str(file_lists[i])
        file_lists=tmp
        with open(datas_path, mode="w") as files:
            files.writelines(file_lists)
            files.close()
        config.read('..\\config.ini')
        path = config.get('PATH','path')
        temp=("imageファイルの保存先を”"+str(config.get('PATH','path'))+"”に変更しました。")
        writeToLog(temp)
    image=tk.Toplevel()
    image.geometry("705x75+500+300")
    image.title("imageの保存先変更")
    image_label=tk.Label(image,text="ファイルパスを絶対パスで設定(\\\\で区切る))", font=("MSゴシック", "13"))
    textBox3=tk.Entry(image,width=117)
    textBox3.place(x=0,y=20)
    button=tk.Button(image,text='決定',command=image_update)
    button.place(x=670,y=50)
    image_label.pack()

def sleeptime_set():
    def sleeptime_update():
        global sleeptime_min,sleeptime_max,sleep_min,sleep_max,sleeptime_min_hour,sleeptime_min_minute,sleeptime_min_second,sleeptime_max_hour,sleeptime_max_minute,sleeptime_max_second,config
        sleeptime_min_hour=int(sleeptimes_combobox.get())
        sleeptime_min_minute=int(sleeptimes_combobox2.get())
        sleeptime_min_second=int(sleeptimes_combobox3.get())
        sleeptime_max_hour=int(sleeptimes_combobox4.get())
        sleeptime_max_minute=int(sleeptimes_combobox5.get())
        sleeptime_max_second=int(sleeptimes_combobox6.get())
        sleep_min=dt.time(sleeptime_min_hour,sleeptime_min_minute,sleeptime_min_second)
        sleep_max=dt.time(sleeptime_max_hour,sleeptime_max_minute,sleeptime_max_second)
        sleeptime_min=str(sleeptime_min_hour)+":"+str(sleeptime_min_minute)+":"+str(sleeptime_min_second)
        sleeptime_max=str(sleeptime_max_hour)+":"+str(sleeptime_max_minute)+":"+str(sleeptime_max_second)
        sleeptime_min_hour_tmp="sleeptime_min_hour="+str(sleeptime_min_hour)
        sleeptime_min_minute_tmp="sleeptime_min_minute="+str(sleeptime_min_minute)
        sleeptime_min_second_tmp="sleeptime_min_second="+str(sleeptime_min_second)
        sleeptime_max_hour_tmp="sleeptime_max_hour="+str(sleeptime_max_hour)
        sleeptime_max_minute_tmp="sleeptime_max_minute="+str(sleeptime_max_minute)
        sleeptime_max_second_tmp="sleeptime_max_second="+str(sleeptime_max_second)
        sleeptime_list=[sleeptime_min_hour_tmp,sleeptime_min_minute_tmp,sleeptime_min_second_tmp,sleeptime_max_hour_tmp,sleeptime_max_minute_tmp,sleeptime_max_second_tmp]
        try:
            with open(datas_path,mode="r") as files:
                file_lists=files.read().split("\n")
                files.close()
            for i in range(6):
                line_num_sleep=i+14
                file_lists[line_num_sleep]=sleeptime_list[i]
            len_file=len(file_lists)
            for i in range(len_file):
                if i==0:
                    tmp=str(file_lists[i])
                else:
                    tmp=str(tmp)+str("\n")+str(file_lists[i])
            file_lists=tmp
            with open(datas_path, mode="w") as files:
                files.writelines(file_lists)
                files.close()
            config.read('..\\config.ini')
        except Exception as e:
            writeToLog("*****Error*****")
            writeToLog(e)
        now_sleeptime['text']="現在の休止時間　"+str(sleeptime_min)+"~"+str(sleeptime_max)
        writeToLog("現在の休止時間を"+sleeptime_min+"~"+sleeptime_max+"に変更しました。")
    sleeptimes=tk.Toplevel()
    sleeptimes.geometry("300x100")
    sleeptimes.title("休止時間の変更")
    sleeptimes_label=tk.Label(sleeptimes,text="休止時間の開始", font=("MSゴシック", "13"))
    sleeptimes_label.place(x=0,y=0)
    sleeptimes_combobox=ttk.Combobox(master=sleeptimes,values=hour_list,height=6, width=2, justify="center",state="readonly")
    sleeptimes_combobox.place(x=0,y=20)
    sleeptimes_combobox2=ttk.Combobox(master=sleeptimes,values=minute_list,height=10, width=2, justify="center",state="readonly")
    sleeptimes_combobox2.place(x=40,y=20)
    sleeptimes_combobox3=ttk.Combobox(master=sleeptimes,values=second_list,height=10, width=2, justify="center",state="readonly")
    sleeptimes_combobox3.place(x=80,y=20)
    sleeptime_label2=tk.Label(sleeptimes,text="~", font=("MSゴシック", "13"))
    sleeptime_label2.place(x=136,y=20)
    sleeptimes_combobox4=ttk.Combobox(master=sleeptimes,values=hour_list,height=6, width=2, justify="center",state="readonly")
    sleeptimes_combobox4.place(x=160,y=20)
    sleeptimes_combobox5=ttk.Combobox(master=sleeptimes,values=minute_list,height=10, width=2, justify="center",state="readonly")
    sleeptimes_combobox5.place(x=200,y=20)
    sleeptimes_combobox6=ttk.Combobox(master=sleeptimes,values=second_list,height=10, width=2, justify="center",state="readonly")
    sleeptimes_combobox6.place(x=240,y=20)
    now_sleeptime = tk.Label(sleeptimes,text="現在の休止時間　"+str(sleeptime_min)+"~"+str(sleeptime_max), font=("MSゴシック", "13", "bold"))
    now_sleeptime.place(x=0,y=40)
    button = tk.Button(sleeptimes,text="decision",command=sleeptime_update)
    button.place(x=250,y=70)

def announcement():
    def announcement_ok():
        send_announcement1=textBox1.get()
        send_announcement1=str(send_announcement1)
        send_announcement1=send_announcement1.replace('$', "\n")
        send_announcement="アナウンス"+"\n"+send_announcement1
        tokens={'Authorization': 'Bearer'+' '+TOKEN}
        send_data={'message': send_announcement}
        requests.post(api_url, headers=tokens, data=send_data)
        writeToLog("送信完了")
        writeToLog(send_announcement)
    announcements=tk.Toplevel()
    announcements.geometry("705x75+500+300")
    announcements.title("Announcements")
    announcement_label=tk.Label(announcements,text="送信テキスト(改行は $ を入力)", font=("MSゴシック", "13"))
    textBox1=tk.Entry(announcements,width=117)
    textBox1.place(x=0,y=20)
    button=tk.Button(announcements,text='送信',command=announcement_ok)
    button.place(x=670,y=50)
    announcement_label.pack()

def stop_time():
    def stop_time_in():
        def stop_count():
            def stop_update():
                global sleep_time
                times=stop_times_combo.get()
                times=int(times)
                second_count=int(times*60)
                sleep_time=second_count
                while True:
                    if second_count>=3600:
                        hour=int(second_count/60/60)
                        minute=int((second_count-(hour*60*60))/60)
                        second=int((((second_count-(hour*60*60))/60)-minute)*60)
                    else:
                        hour=0
                        minute=int(second_count/60)
                        if minute<1:
                            minute=0
                            second=int(second_count)
                        else:
                            second=int(((second_count/60)-minute)*60)
                    stop_times_label2['text']="残り"+str(hour)+"時間"+str(minute)+"分"+str(second)+"秒で再開"
                    if second%10==0 and second==0:
                        tmp="残り"+str(hour)+"時間"+str(minute)+"分"+str(second)+"秒で再開"
                        writeToLog(tmp)
                        tmp=0
                    second_count-=1
                    if second_count==0:
                        writeToLog("再開")
                        break
                    time.sleep(1)

            thread_3=threading.Thread(target=stop_update)
            thread_3.setDaemon(True)
            thread_3.start()
        stop_times=tk.Toplevel()
        stop_times.geometry("300x120")
        stop_times.title("Stop Time")
        stop_times_combo=ttk.Combobox(master=stop_times,values=stop_time_list,height=10, width=4, justify="center",state="readonly")
        stop_times_combo.place(x=20,y=20)
        stop_times_label = tk.Label(stop_times,text="一時休止時間設定", font=("MSゴシック", "13", "bold"))
        stop_times_label.place(x=0,y=40)
        stop_times_label2=tk.Label(stop_times,text="残り"+"None"+"時間"+"None"+"分"+"None"+"秒で再開", font=("MSゴシック", "13", "bold"))
        stop_times_label2.place(x=0,y=60)
        stop_times_button=tk.Button(stop_times,text="決定",command=stop_count)
        stop_times_button.place(x=270,y=90)

    thread_2=threading.Thread(target=stop_time_in)
    thread_2.setDaemon(True)
    thread_2.start()


#画像ダウンロード関数
def file_download(p,list_len_json,json_ronse,media_keys,list_len):
    global path,data_presence_or_absence,download_failed
    media_keys2=media_keys[p]
    media_keys2=str(media_keys2)
    media_keys2=media_keys2.lstrip("['")
    media_keys2=media_keys2.removesuffix("']")
    temp=("media_keys:",media_keys)
    writeToLog(temp)
    for h in range(list_len_json):
        json_romse_check=json_ronse['includes']['media'][h]['media_key']
        writeToLog(json_romse_check)
        if json_romse_check == media_keys2:
            writeToLog("ok")
            json_ronse_data_media=json_ronse['includes']['media'][h]
            writeToLog(json_ronse_data_media)
            if json_ronse_data_media['type'] == 'photo':
                img_url = json_ronse_data_media['url']
                file_name=path+"\\"+str(p)+".jpg"
                #画像のダウンロード
                ronse = requests.get(img_url)
                image = ronse.content
                with open(file_name, "wb") as aaa:
                    aaa.write(image)
                    aaa.close()
            elif json_ronse_data_media['type'] == 'video':
                #videoだったらスキップ
                writeToLog("This download key is video")
                data_presence_or_absence="no"
                list_len=list_len-1
            break
        elif json_romse_check != media_keys2:
            writeToLog("Download key is not the same")
            data_presence_or_absence="no"
        else:
            writeToLog("*****Download failed*****")
            download_failed=download_failed+1
            try:
                download_failed_error['text']="download failed "+str(download_failed)+"回"
            except:
                pass
            data_presence_or_absence="no"
    return list_len

#検索エンドポイントに接続してJSONを取得する関数
def connect_to_endpoint(url, params):
    global status_code_is_not_200
    #APIを叩いて結果を取得
    ronse = requests.get(url, auth=bearer_oauth, params=params)
    #ステータスコードが200以外ならエラー処理
    if ronse.status_code != 200:
        writeToLog("*****status code is not 200*****")
        status_code_is_not_200=status_code_is_not_200+1
        try:
            status_code_is_not_200_error['text']="status code is not 200 "+str(status_code_is_not_200)+"回"
        except:
            pass
        raise Exception(ronse.status_code, ronse.text)

    #ronseからJSONを取得してループを回し、URLを追加していく
    json_ronse = ronse.json()
    json_ronse_data1=(json_ronse['data'][0])
    writeToLog(json_ronse_data1)
    global tweets_data1
    tweets_data1=json_ronse_data1
    #画像があるかの判別
    keys="attachments" in json_ronse_data1
    writeToLog(keys)
    if keys==True:
        data_presence_or_absence="yes"
        media_keys=(json_ronse_data1['attachments']['media_keys'])
        list_len=(len(media_keys))
        list_len_json=(len(json_ronse['includes']['media']))
        #media_keysの取得
        list_len_json=list_len_json
        writeToLog(list_len_json)
        writeToLog("keys=yes")
        return data_presence_or_absence,json_ronse_data1,list_len,list_len_json,json_ronse,media_keys
    elif keys==False:
        data_presence_or_absence="no"
        list_len_json=0
        media_keys=False
        writeToLog("media_keys=None")
        list_len=0
        return data_presence_or_absence,json_ronse_data1,list_len,list_len_json,json_ronse,media_keys
    else:
        writeToLog("*****Media_key is not the same*****")

#日本時間に変更する関数
def change_time_JST(u_time):
    #イギリスのtimezoneを設定するために再定義する
    utc_time = dt.datetime(u_time.year, u_time.month,u_time.day, \
    u_time.hour,u_time.minute,u_time.second, tzinfo=dt.timezone.utc)
    #タイムゾーンを日本時刻に変換
    jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
    # 文字列で返す
    str_time = jst_time.strftime("%Y-%m-%d_%H:%M:%S")
    return str_time
#抽出したデータから必要な情報を取り出す

#main関数
def main():
    def quit():
        errors.destroy()
    time.sleep(1)
    global number_of_trials,network_not_found,number_of_executions_count,sleep_time
    while True:
        nowtime=dt.datetime.now()
        nowtime=nowtime.time()
        if nowtime>=sleep_min and nowtime<=sleep_max:
            pass
            tmp="nowtime is "+sleeptime_min+"~"+sleeptime_max
            writeToLog(tmp)
            time.sleep(sleep_time)
        else:
            number_of_executions_count=number_of_executions_count+1
            try:
                number_of_executions['text']="number of executions "+str(number_of_executions_count)+"回"
            except:
                pass
            try:
                #tweetの取得
                data_presence_or_absence,json_ronse_data1,list_len,list_len_json,json_ronse,media_keys = connect_to_endpoint(search_url, query_params)
                writeToLog(data_presence_or_absence)
                writeToLog(dt.datetime.now())
                # ronse クラスの中身は https://docs.tweepy.org/en/stable/ronse.html#tweepy.ronse
                #検出されたtweetをtxtに入力
                f = open(tweet_text_now_file, 'w', encoding='utf-8')
                f.write(json_ronse_data1['text'])
                f.close()
                with open(tweet_text_now_file,'r',encoding="utf-8_sig") as f:
                    file_read = f.read()
                    f.close()
                if os.path.exists(tweet_text_file)==True:
                    with open(tweet_text_file,'r',encoding="utf-8_sig") as f:
                        file_read1 = f.read()
                        f.close()
                elif os.path.exists(tweet_text_file)==False:
                    f=open(tweet_text_file,'w',encoding="utf-8")
                    f.write("")
                    f.close()
                    with open(tweet_text_file,'r',encoding="utf-8_sig") as f:
                        file_read1 = f.read()
                        f.close()
                #print(file_read1)
                #print(file_read1)
                #txtの内容の確認
                if file_read == file_read1:
                    writeToLog("file:True")
                elif file_read != file_read1:
                    number_of_trials=0
                    writeToLog("file:False")
                    #tweet時刻の取得
                    tweets = tweepy.Cursor(api.search_tweets,q=search_word,lang='ja').items(item_num)
                    #取得したツイートを一つずつ取り出して必要な情報をtweet_dataに格納する
                    tweets_data = []
                    for tweets2 in tweets:
                        #ツイート時刻とユーザのアカウント作成時刻を日本時刻にする
                        tweet_time = change_time_JST(tweets2.created_at)
                    if list_len==1:
                        for p in range(1):
                            list_len=file_download(p,list_len_json,json_ronse,media_keys,list_len)
                    elif list_len==2:
                        for p in range(2):
                            list_len=file_download(p,list_len_json,json_ronse,media_keys,list_len)
                    elif list_len==3:
                        for p in range(3):
                            list_len=file_download(p,list_len_json,json_ronse,media_keys,list_len)
                    elif list_len==4:
                        for p in range(4):
                            list_len=file_download(p,list_len_json,json_ronse,media_keys,list_len)
                    writeToLog("===================")
                    #print("Tweet id:", json_ronse_data1['id'])
                    temp=("Tweet text:", json_ronse_data1['text'])
                    writeToLog(temp)
                    temp=("Tweet time:",tweet_time)
                    writeToLog(temp)
                    f = open(tweet_text_file, 'w', encoding='utf-8')
                    f.write(json_ronse_data1['text'])
                    f.close()
                    #LINE Notifyに送信する準備
                    tweet_text=json_ronse_data1['text']
                    send_contents0 = f'@Genshin_7の最新ツイートのお知らせ\nツイートされた時刻 {tweet_time}\n{tweet_text}\n'
                    send_contents = f'@Genshin_7の最新ツイートのお知らせ\nツイートされた時刻 {tweet_time}\n{tweet_text}\n1枚目\n'
                    TOKEN_dic = {'Authorization': 'Bearer'+' '+TOKEN}
                    send_dic0 = {'message': send_contents0}
                    send_dic={'message': send_contents}
                    data0={'content': send_contents0}
                    data={'content': send_contents}
                    send_contents1 = f'2枚目'
                    send_contents2 = f'3枚目'
                    send_contents3 = f'4枚目'
                    send_dic1= {'message':send_contents1}
                    send_dic2= {'message':send_contents2}
                    send_dic3= {'message':send_contents3}
                    data1= {'message':send_contents1}
                    data2= {'message':send_contents2}
                    data3= {'message':send_contents3}
                    image_file=path+"\\"+'0.jpg'
                    image_file1=path+"\\"+'1.jpg'
                    image_file2=path+"\\"+'2.jpg'
                    image_file3=path+"\\"+'3.jpg'
                    #画像数の判別
                    if data_presence_or_absence=="yes":
                        if list_len==1:
                            binary=open(image_file,mode='rb')
                            image_dic = {'imageFile':binary}
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                            writeToLog("LINE:送信完了")
                            with open(image_file,'rb') as f:
                                file_bin=f.read()
                                f.close()
                            files={"favicon":(image_file,file_bin)}
                            requests.post(disc_web_url, data=data,files=files)
                            writeToLog("Discord:送信完了")
                        elif list_len==2:
                            binary=open(image_file,mode='rb')
                            image_dic = {'imageFile':binary}
                            binary1=open(image_file1,mode='rb')
                            image_dic1={'imageFile':binary1}
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                            requests.post(api_url,headers=TOKEN_dic,data=send_dic1,files=image_dic1)
                            writeToLog("LINE:送信完了")
                            with open(image_file,'rb') as f:
                                file_bin=f.read()
                                f.close()
                            files={"favicon":(image_file,file_bin)}
                            requests.post(disc_web_url, data=data,files=files)
                            with open(image_file1,'rb') as g:
                                file_bin2=g.read()
                                g.close()
                            files2={"favicon":(image_file1,file_bin2)}
                            requests.post(disc_web_url, data=data1,files=files2)
                            writeToLog("Discord:送信完了")
                        elif list_len==3:
                            binary=open(image_file,mode='rb')
                            image_dic = {'imageFile':binary}
                            binary1=open(image_file1,mode='rb')
                            image_dic1={'imageFile':binary1}
                            binary2=open(image_file2,mode='rb')
                            image_dic2={'imageFile':binary2}
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic1,files=image_dic1)
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic2,files=image_dic2)
                            writeToLog("LINE:送信完了")
                            with open(image_file,'rb') as f:
                                file_bin=f.read()
                                f.close()
                            files={"favicon":(image_file,file_bin)}
                            requests.post(disc_web_url, data=data,files=files)
                            with open(image_file1,'rb') as g:
                                file_bin2=g.read()
                                g.close()
                            files2={"favicon":(image_file1,file_bin2)}
                            requests.post(disc_web_url, data=data1,files=files2)
                            with open(image_file2,'rb') as h:
                                file_bin3=h.read()
                                h.close()
                            files3={"favicon":(image_file2,file_bin3)}
                            requests.post(disc_web_url, data=data2,files=files3)
                            writeToLog("Discord:送信完了")
                        elif list_len==4:
                            binary=open(image_file,mode='rb')
                            image_dic = {'imageFile':binary}
                            binary1=open(image_file1,mode='rb')
                            image_dic1={'imageFile':binary1}
                            binary2=open(image_file2,mode='rb')
                            image_dic2={'imageFile':binary2}
                            binary3=open(image_file3,mode='rb')
                            image_dic3={'imageFile':binary3}
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic,files=image_dic)
                            requests.post(api_url,headers=TOKEN_dic,data=send_dic1,files=image_dic1)
                            requests.post(api_url,headers=TOKEN_dic,data=send_dic2,files=image_dic2)
                            requests.post(api_url,headers=TOKEN_dic,data=send_dic3,files=image_dic3)
                            writeToLog("LINE:送信完了")
                            with open(image_file,'rb') as f:
                                file_bin=f.read()
                                f.close()
                            files={"favicon":(image_file,file_bin)}
                            requests.post(disc_web_url, data=data,files=files)
                            with open(image_file1,'rb') as g:
                                file_bin2=g.read()
                                g.close()
                            files2={"favicon":(image_file1,file_bin2)}
                            requests.post(disc_web_url, data=data1,files=files2)
                            with open(image_file2,'rb') as h:
                                file_bin3=h.read()
                                h.close()
                            files3={"favicon":(image_file2,file_bin3)}
                            requests.post(disc_web_url, data=data2,files=files3)
                            with open(image_file3,'rb') as i:
                                file_bin4=i.read()
                                i.close()
                            files4={"favicon":(image_file3,file_bin4)}
                            requests.post(disc_web_url, data=data3,files=files4)
                            writeToLog("Discord:送信完了")
                        else:
                            requests.post(api_url, headers=TOKEN_dic, data=send_dic0)
                            writeToLog("LINE:送信完了")
                            requests.post(disc_web_url, data=data0)
                            writeToLog("Discord:送信完了")
                    elif data_presence_or_absence=="no":
                        requests.post(api_url, headers=TOKEN_dic, data=send_dic0)
                        writeToLog("LINE:送信完了")
                        requests.post(disc_web_url, data=data0)
                        writeToLog("Discord:送信完了")
                    files_error=False
                #待機秒数
                if number_of_trials<=11:
                    time.sleep(3)
                    number_of_trials=number_of_trials+1
                else:
                    time.sleep(sleep_time)
            #networkエラーなどの処理
            except Exception as e:
                es=str(e)
                if "No such file or directory" in es:
                    writeToLog("*****Error*****")
                    writeToLog("*****FileNotFoundError*****")
                    errors=tk.Toplevel()
                    errors.geometry("280x100+500+300")
                    errors.title("Error")
                    error_label=tk.Label(errors,text="入力されたディレクトリが存在しません。\n入力し直してください。", font=("MSゴシック", "13"))
                    error_label.place(x=0,y=0)
                    error_ok=tk.Button(errors,text="OK",command=quit)
                    error_ok.place(x=250,y=70)
                else:
                    writeToLog("*****Error*****")
                    writeToLog("*****network not found*****")
                    writeToLog(e)
                    network_not_found=network_not_found+1
                try:
                    network_not_found_error['text']="network not found "+str(network_not_found)+"回"
                except:
                    pass
                time.sleep(sleep_time)
                pass

def discord_main():
    def json_out(uid):
        global r
        logs="uid:"+str(uid)
        uid=int(uid)
        url=f"https://enka.network/u/{uid}/__data.json"
        r=requests.get(url)
        r=r.json()
        with open("uid-data.txt","w",encoding="utf-8") as f:
            f.write(str(r))
            f.close()
        return url
    class uid_modal(discord.ui.Modal,title="UIDを入力してください"):
        answer = discord.ui.TextInput(label='UID',min_length=9,max_length=9)
        async def on_submit(self,ctx:discord.Interaction):
            uid=str(self.answer.value)
            print(uid)
            writeToLog_discord(uid)
            async with ctx.channel.typing():
                await ctx.response.send_message(content="アカウント情報読み込み中...")
                url_enka=json_out(uid)
                try:
                    embed = discord.Embed(title=f"{r['playerInfo']['nickname']}の原神ステータス",color=0x1e90ff,description=f"UID: {uid}",url=url_enka)
                    avater_id = str(r['playerInfo']['profilePicture']['avatarId'])
                    side_icon=charactersEN[avater_id]['SideIconName']
                    main_icon=side_icon.replace('UI_AvatarIcon_Side_', '')
                    main_icon="UI_AvatarIcon_"+main_icon
                    try:
                        embed.set_thumbnail(url=f"https://enka.network/ui/{main_icon}.png")
                    except:
                        pass
                    try:
                        embed.add_field(inline=False,name="ステータスメッセージ",value=r['playerInfo']['signature'])
                    except:
                        writeToLog_discord("Error")
                    embed.add_field(inline=False,name="冒険ランク",value=r['playerInfo']['level'])
                    embed.add_field(inline=False,name="世界ランク",value=r['playerInfo']['worldLevel'])
                    embed.add_field(inline=False,name="アチーブメント",value=r['playerInfo']['finishAchievementNum'])
                    embed.add_field(inline=False,name="深境螺旋",value=f"第{r['playerInfo']['towerFloorIndex']}層 第{r['playerInfo']['towerLevelIndex']}間")
                except:
                    embed = discord.Embed(title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\nUIDが間違っている可能性があります。\n{url_enka}",color=0xff0000,url=url_enka)
                await ctx.channel.send(content="キャラ情報読み込み中...")
                try:
                    #改良
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url_enka) as response:
                            resp = await response.json()
                            resalt = []
                    for id in resp["playerInfo"]["showAvatarInfoList"]:
                        resalt.append(id["avatarId"])
                    tmp=[]
                    for i in range(len(resalt)):
                        tmp_resalt=str(resalt[i])
                        tmp.append(charactersJP['characters'][tmp_resalt]['name'])
                    args=[]
                    for i in range(len(tmp)):
                        args.append(tmp[i])
                    await ctx.channel.send(content=None,embed=embed)
                    await ctx.channel.send('',view=HogeButton(args))
                except Exception as e:
                    writeToLog_discord("*****Error*****")
                    writeToLog_discord(e)
                    embed = discord.Embed(title="エラー",color=0xff0000,description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。",url=url_enka)
                    await ctx.channel.send(content=None,embed=embed)
                await ctx.response.send_message(content=None,embed=embed)
    class HogeButton(discord.ui.View):
        def __init__(self,args):
            super().__init__()
            for txt in args:
                self.add_item(HugaButton(txt))
    class HugaButton(discord.ui.Button):
        def __init__(self,txt:str):
            super().__init__(label=txt,style=discord.ButtonStyle.red)

        async def callback(self,interaction:discord.Interaction):
            global id_chara
            tmp=f'{self.label}が選択されました'
            chara_name=str(self.label)
            await interaction.response.send_message(tmp)
            for key,item1 in charactersJP.items():
                if key=="characters":
                    for key1,item2 in item1.items():
                        for key2,item3 in item2.items():
                            if key2=="name":
                                if item3==chara_name:
                                    id_chara=key1
            #uidのlocalのErrorの解消,id_charaの算出方法の見直し
            uid=int(r['uid'])
            url = f"https://enka.network/u/{uid}/__data.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    resp = await response.json()
            name =chara_name
            id_chara = int(id_chara)
            try:
                for n in resp['avatarInfoList']:
                    if n["avatarId"] == id_chara:
                        chara = n
                        break
                    else:
                        continue
                for n in resp['playerInfo']["showAvatarInfoList"]:
                    if n["avatarId"] == id_chara:
                        level = n["level"]
                        break
                    else:
                        continue
            except:
                embed = discord.Embed(title="エラー",color=0xff0000,description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。", url=url)
                return embed
            try:
                embed = discord.Embed(title=name,color=0x1e90ff,description=f"{level}lv",url=url)
                hoge = charactersJP['characters'][str(id_chara)]["sideIconName"]
                embed.set_thumbnail(url=f"https://enka.network/ui/{hoge}.png")
                embed.add_field(inline=True,name="キャラレベル",value=f"{level}lv")
                if "talentIdList" in chara:
                    totu=len(chara['talentIdList'])
                else:
                    totu="無"
                tmp_totu=str(totu)+"凸"
                embed.add_field(inline=True,name="凸数",value=tmp_totu)
                embed.add_field(inline=True,name="HP上限",
                    value=f'{str(round(chara["fightPropMap"]["2000"]))}'
                )
                embed.add_field(inline=True,name="攻撃力",
                    value=f'{str(round(chara["fightPropMap"]["2001"]))}'
                )
                embed.add_field(inline=True,name="防御力",
                    value=f'{str(round(chara["fightPropMap"]["2002"]))}'
                )
                embed.add_field(inline=True,name="会心率",
                    value=f'{str(round(chara["fightPropMap"]["20"] *100))}%'
                )
                embed.add_field(inline=True,name="会心ダメージ",
                    value=f'{str(round(chara["fightPropMap"]["22"]*100))}%'
                )
                embed.add_field(inline=True,name="元素チャージ効率",
                    value=f'{str(round(chara["fightPropMap"]["23"]*100))}%'
                )
                embed.add_field(inline=True,name="元素熟知",
                    value=f'{str(round(chara["fightPropMap"]["28"]))}'
                )
                buf = 1
                if round(chara["fightPropMap"]["30"]*100) > 0:
                    embed.add_field(inline=True,name="物理ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["30"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["30"])
                elif round(chara["fightPropMap"]["40"]*100) > 0:
                    embed.add_field(inline=True,name="炎元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["40"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["40"])
                elif round(chara["fightPropMap"]["41"]*100) > 0:
                    embed.add_field(inline=True,name="雷元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["41"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["41"])
                elif round(chara["fightPropMap"]["42"]*100) > 0:
                    embed.add_field(inline=True,name="水元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["42"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["42"])
                elif round(chara["fightPropMap"]["43"]*100) > 0:
                    embed.add_field(inline=True,name="草元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["43"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["42"])
                elif round(chara["fightPropMap"]["44"]*100) > 0:
                    embed.add_field(inline=True,name="風元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["44"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["44"])
                elif round(chara["fightPropMap"]["45"]*100) > 0:
                    embed.add_field(inline=True,name="岩元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["45"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["45"])
                elif round(chara["fightPropMap"]["46"]*100) > 0:
                    embed.add_field(inline=True,name="氷元素ダメージ",
                        value=f'{str(round(chara["fightPropMap"]["46"]*100))}%'
                    )
                    buf += round(chara["fightPropMap"]["46"])
                temp = []
                for myvalue in chara["skillLevelMap"].values():
                    temp.append(f"{myvalue}")
                embed.add_field(inline=False,name="天賦レベル",
                    value="\n".join(temp)
                )
                embed.add_field(inline=False,name="好感度",
                    value=chara['fetterInfo']['expLevel']
                )
                weapon_true='weaponStats'
                name_sei_list=[]
                total_score=0
                for n in chara["equipList"]:
                    if weapon_true in n['flat']:
                        weapon_level=n['weapon']['level']
                        weapon_name=n['flat']['nameTextMapHash']
                        for k,x in charactersJP['weapons'].items():
                            if weapon_name==k:
                                weapon_name=x
                                break
                        weapon_main=n['flat']['weaponStats'][0]['appendPropId']
                        weapon_main_value=n['flat']['weaponStats'][0]['statValue']
                        weapon_sub=n['flat']['weaponStats'][1]['appendPropId']
                        weapon_sub_value=n['flat']['weaponStats'][1]['statValue']
                        #iconはいつか実装
                        weapon_icon=n['flat']['icon']
                        weapon_main=charactersJP['equip_stat'][weapon_main]
                        weapon_sub=charactersJP['equip_stat'][weapon_sub]
                        embed.add_field(inline=True,name=f'武器:{weapon_name}',value=f'{weapon_level}lv\n{weapon_main}:{weapon_main_value}\n{weapon_sub}:{weapon_sub_value}')
                    else:
                        for k,x in charactersJP['weapons'].items():
                            name_hash=n['flat']['setNameTextMapHash']
                            if name_hash==k:
                                name_sei=x
                                break
                        equip=n['flat']['equipType']
                        equip=charactersJP['equip'][equip]
                        main_equip=n["flat"]["reliquaryMainstat"]["mainPropId"]
                        main_equip=charactersJP['equip_stat'][main_equip]
                        hoge=[]
                        score_sei=0
                        for b in n["flat"]["reliquarySubstats"]:
                            name_=b["appendPropId"]
                            name_=charactersJP['equip_stat'][name_]
                            value_=b["statValue"]
                            score_value=float(value_)
                            if name_=="会心率":
                                score_sei=score_sei+(score_value*2)
                            elif name_=="会心ダメージ":
                                score_sei=score_sei+score_value
                            elif name_=="攻撃力%":
                                score_sei=score_sei+score_value
                            hoge.append(f"{name_}:{value_}")
                        name_sei_list.append(name_sei)
                        score_sei=round(score_sei,2)
                        total_score=total_score+score_sei
                        embed.add_field(inline=True,name=f'聖遺物：{equip}\n{name_sei}\n{main_equip}:{n["flat"]["reliquaryMainstat"]["statValue"]}\n{n["reliquary"]["level"]-1}lv\n---スコア:{score_sei}---\n',
                            value="\n".join(hoge)
                        )
                total_score=round(total_score,2)
                embed.add_field(inline=True,name="トータルスコア:",value=total_score)
                name_sei_count=collections.Counter(name_sei_list)
                key_count_num=0
                value_count_4="aaa"
                value_count_2_1="aaa"
                value_count_2_2="aaa"
                set_equip="aaa"
                set_equip1="aaa"
                set_equip2="aaa"
                for key_count,value_count in name_sei_count.items():
                    value_count_int=int(value_count)
                    if value_count_int>=4:
                        value_count_4=key_count
                    elif value_count_int>=2 and key_count_num==0:
                        value_count_2_1=key_count
                        key_count_num+=1
                    elif value_count_int>=2 and key_count_num==1:
                        value_count_2_2=key_count
                if not value_count_4=="aaa":
                    set_equip=value_count_4
                elif not value_count_2_1=="aaa":
                    set_equip1=value_count_2_1
                    if not value_count_2_2=="aaa":
                        set_equip2=value_count_2_2
                score_sei=round(score_sei,2)
                set_list=[]
                if not set_equip=="aaa":
                    set_list.append(f"4セット:{set_equip}")
                elif not set_equip1=="aaa":
                    set_list.append(f"2セット:{set_equip1}")
                    if not set_equip2=="aaa":
                        set_list.append(f"2セット:{set_equip2}")
                embed.add_field(inline=True,name="セット効果",value="\n".join(set_list))
                await interaction.channel.send(content=None,embed=embed)
            except KeyError:
                embed = discord.Embed(title="エラー",color=0xff0000,description=f"エラー", url=url)
                await interaction.channel.send(content=None,embed=embed)
            await interaction.channel.send("この先は開発中です")
    class HogeList(discord.ui.View):
        def __init__(self,args):
            super().__init__()
            self.add_item(HugaList(args))
    class HugaList(discord.ui.Select):
        def __init__(self,args):
            options=[]
            for item in args:
                options.append(discord.SelectOption(label=item, description=''))
            super().__init__(placeholder='', min_values=1, max_values=1, options=options)
        async def callback(self,ctx:discord.Interaction):
            if self.values[0]=="UIDを入力する":
                await ctx.response.send_modal(uid_modal())
            elif self.values[0]=="登録してあるUIDを使う":
                uid_list_in=ctx.user.mention in uid_list
                if uid_list_in == True:
                    uid=str(uid_list[ctx.user.mention])
                    if len(uid) == 9:
                        writeToLog_discord(uid)
                        async with ctx.channel.typing():
                            await ctx.response.send_message(content="アカウント情報読み込み中...")
                            url_enka=json_out(uid)
                            try:
                                embed = discord.Embed(title=f"{r['playerInfo']['nickname']}の原神ステータス",color=0x1e90ff,description=f"UID: {uid}",url=url_enka)
                                avater_id = str(r['playerInfo']['profilePicture']['avatarId'])
                                side_icon=charactersEN[avater_id]['SideIconName']
                                main_icon=side_icon.replace('UI_AvatarIcon_Side_', '')
                                main_icon="UI_AvatarIcon_"+main_icon
                                try:
                                    embed.set_thumbnail(url=f"https://enka.network/ui/{main_icon}.png")
                                except:
                                    pass
                                try:
                                    embed.add_field(inline=False,name="ステータスメッセージ",value=r['playerInfo']['signature'])
                                except:
                                    writeToLog_discord("Error")
                                embed.add_field(inline=False,name="冒険ランク",value=r['playerInfo']['level'])
                                embed.add_field(inline=False,name="世界ランク",value=r['playerInfo']['worldLevel'])
                                embed.add_field(inline=False,name="アチーブメント",value=r['playerInfo']['finishAchievementNum'])
                                embed.add_field(inline=False,name="深境螺旋",value=f"第{r['playerInfo']['towerFloorIndex']}層 第{r['playerInfo']['towerLevelIndex']}間")
                            except:
                                embed = discord.Embed(title=f"エラーが発生しました。APIを確認してからもう一度お試しください。\nUIDが間違っている可能性があります。\n{url_enka}",color=0xff0000,url=url_enka)
                            await ctx.channel.send(content="キャラ情報読み込み中...")
                            try:
                                #改良
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(url_enka) as response:
                                        resp = await response.json()
                                        resalt = []
                                for id in resp["playerInfo"]["showAvatarInfoList"]:
                                    resalt.append(id["avatarId"])
                                tmp=[]
                                for i in range(len(resalt)):
                                    tmp_resalt=str(resalt[i])
                                    tmp.append(charactersJP['characters'][tmp_resalt]['name'])
                                args=[]
                                for i in range(len(tmp)):
                                    args.append(tmp[i])
                                await ctx.channel.send(content=None,embed=embed)
                                await ctx.channel.send('',view=HogeButton(args))
                            except Exception as e:
                                writeToLog_discord("*****Error*****")
                                writeToLog_discord(e)
                                embed = discord.Embed(title="エラー",color=0xff0000,description=f"キャラ詳細が非公開です。原神の設定で公開設定にしてください。",url=url_enka)
                                await ctx.channel.send(content=None,embed=embed)
                    else:
                        embed = discord.Embed(title="エラー",color=0xff0000,description=f"登録されているUIDはUIDではありません。もしくはUIDが間違っています。")
                        await ctx.response.send_message(content=None,embed=embed)
                else:
                    await ctx.response.send_message(content="DiscordアカウントとUIDが紐付けられていません。\n紐づけてからお使いください。")
    try:
        channel = client.get_channel(channel_id)
        every=1050429151804407899
        server=1049947800928002089
        @tree.command(name="get",description="UIDからキャラ情報を取得します。")
        async def select(ctx:discord.Interaction):
            writeToLog_discord("run get")
            writeToLog_discord(ctx.user.mention)
            writeToLog_discord("------------")
            args=["UIDを入力する","登録してあるUIDを使う"]
            await ctx.response.send_message(content="",view=HogeList(args))
        @tree.command(name="uid_registration",description="DiscordアカウントとUIDを紐づけます。")
        async def gets(ctx0:discord.Interaction,uid:str):
            global uid_list
            writeToLog_discord("run uid registration")
            writeToLog_discord(ctx0.user.mention)
            writeToLog_discord("------------")
            if len(uid) == 9:
                await ctx0.response.send_message(content=f"{uid}をアカウントと紐づけます。")
                async with ctx0.channel.typing():
                    try:
                        user_id_dis=ctx0.user.mention
                        uid_list[str(user_id_dis)]=int(uid)
                        writeToLog_discord(uid_list)
                        with open("uid-list.json","w") as f:
                            json.dump(uid_list,f)
                            f.close()
                        await ctx0.channel.send(content="登録が完了しました。")
                    except:
                        embed = discord.Embed(title="エラーが発生しました。",color=0xff0000)
                        await ctx0.response.send_message(content=None,embed=embed)
            else:
                embed = discord.Embed(title="UIDが間違っている可能性があります。",color=0xff0000,description=f"UIDではありません。もしくはUIDが間違っています。")
                await ctx0.response.send_message(content=None,embed=embed)
        @tree.command(name="come",description="プレイヤーにメンションを送ります。")
        async def come(ctx4:discord.Interaction):
            await ctx4.response.send_message('<@&{}> {} が七聖召喚の相手を探してるよ。\n参加してあげよう!'.format(every,ctx4.user.mention))
            writeToLog_discord("run come")
            writeToLog_discord(ctx4.user.mention)
            writeToLog_discord("------------")
        @tree.command(name="version",description="Genshin_Informationのバージョンを表示します。")
        async def versions(ctx2:discord.Interaction):
            await ctx2.response.send_message('{}'.format(version))
            writeToLog_discord("run version")
            writeToLog_discord(ctx2.user.mention)
            writeToLog_discord("------------")
        @tree.command(name="help",description="helpを表示します。")
        async def helps(ctx3:discord.Interaction):
            await ctx3.response.send_message('-----ALL Commands-----\n/getを入力するとUIDからキャラ情報を取得します。\n/comeを入力するとプレイヤーに七聖召喚の募集を行います。\n/versionを入力するとGenshin_Informationのバージョンを表示します。\n/helpを入力するとhelpを表示します。\nuid registrationを入力するとDiscordアカウントとUIDを紐づけます。')
            writeToLog_discord("run help")
            writeToLog_discord(ctx3.user.mention)
            writeToLog_discord("------------")

        @client.event
        async def on_ready():
            writeToLog_discord(client.user.name)
            writeToLog_discord(client.user.id)
            writeToLog_discord('ログイン完了')
            writeToLog_discord('------------')
            await tree.sync()

    except Exception as e:
        writeToLog_discord("*****Error*****")
        writeToLog_discord(e)

    client.run(discord_token)


if __name__=='__main__':
    t1=time.time()
    try:
        thread_1=threading.Thread(target=main)
        thread_1.setDaemon(True)
        thread_2=threading.Thread(target=discord_main)
        thread_2.setDaemon(True)
        #関数の起動
        thread_1.start()
        thread_2.start()
    except:
        pass
    try:
        #TkinterのGUIの表示
        command=tk.Tk()
        command.geometry("1000x580+700+0")
        command.title("Command")
        error=tk.Toplevel()
        error.geometry("300x100+500+400")
        error.title("Errors")
        count=tk.Toplevel()
        count.geometry("290x30+500+500")
        count.title("Count")
        discord_command=tk.Toplevel()
        discord_command.geometry("1000x580+200+0")
        discord_command.title("Discord command")
        download_failed_error = tk.Label(error,text="download failed "+str(download_failed)+"回", font=("MSゴシック", "15", "bold"))
        status_code_is_not_200_error = tk.Label(error,text="status code is not 200 "+str(status_code_is_not_200)+"回", font=("MSゴシック", "15", "bold"))
        network_not_found_error = tk.Label(error,text="network not found "+str(network_not_found)+"回", font=("MSゴシック", "15", "bold"))
        download_failed_error.pack()
        status_code_is_not_200_error.pack()
        network_not_found_error.pack()
        number_of_executions=tk.Label(count,text="number of executions "+str(number_of_executions_count)+"回", font=("MSゴシック", "15", "bold"))
        number_of_executions.pack()
        frame1=ttk.Frame(command,padding=10)
        frame1.grid()
        log=Text(command,state='disabled',borderwidth=6,width=136,height=43,wrap='none',padx=10,pady=10)
        ys= tk.Scrollbar(command,orient ='vertical',command=log.yview)
        log['yscrollcommand']=ys.set
        log.insert('end',"Lorem ipsum...\n...\n...")
        log.see("end")
        log.grid(row=4,column=0)
        ys.grid(column=1,row=4,sticky='ns')
        frame2=ttk.Frame(command,padding=10)
        frame2.grid()
        log2=Text(discord_command,state='disabled',borderwidth=6,width=136,height=43,wrap='none',padx=10,pady=10)
        ys2= tk.Scrollbar(discord_command,orient ='vertical',command=log2.yview)
        log2['yscrollcommand']=ys.set
        log2.insert('end',"Lorem ipsum...\n...\n...")
        log2.see("end")
        log2.grid(row=4,column=0)
        ys2.grid(column=1,row=4,sticky='ns')
        men=tk.Menu(command)
        command.config(menu=men)
        menu=tk.Menu(command)
        men.add_cascade(label="メニュー",menu=menu)
        cascade_a_1 = tk.Menu(men,tearoff=False)
        menu.add_cascade(label="設定",menu=cascade_a_1)
        cascade_a_1.add_command(label="更新頻度変更",command=menu_update)
        cascade_a_1.add_command(label="一時休止時間設定",command=stop_time)
        cascade_a_1.add_command(label="txtの保存場所変更",command=txt_file)
        cascade_a_1.add_command(label="画像の保存場所変更",command=image_file)
        cascade_a_1.add_command(label="休止時間の変更",command=sleeptime_set)
        menu.add_command(label="稼働時間",command=menu_time)
        menu.add_command(label="アナウンス",command=announcement)
        menu.add_separator()
        menu.add_command(label="Exit",command=lambda:command.destroy())
        command.mainloop()
    except:
        pass
