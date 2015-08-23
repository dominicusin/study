# -*- coding: utf-8
import requests
import time
import ast
from tkinter import *
#https://oauth.vk.com/authorize?client_id=5015702&scope=notify,friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications,stats,ads,offline&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
sleepTime = 1
waitTime = 100
looping = False
photosizes = [2560, 1280, 807, 604, 512, 352, 256, 130, 128, 100, 75, 64]
token_file = open('token_file.txt', 'r') 
token_list = [token[:-1] for token in token_file.readlines() if token[0]!='#'] #start line with # to make it comment
token_file.close()
printm=''
width=0
height=0
mnemonics={}
ignore=[]
token_num=0

def call_api(method, params, token):
        #time.sleep(sleepTime)
        print('.', end='') if not looping else print('.')
        params["access_token"] = token
        params["v"] = "5.35"
        url = "https://api.vk.com/method/" + method
        while True:
                try:
                        result = requests.post(url, data=params).json()
                        return result["response"] if "response" in result else result
                except:
                        print('error')
                        time.sleep(sleepTime)
def read_mnemonics(mnemofile):
        result = {}
        with open(mnemofile) as f:
                for line in f:
                        key, value = line.split()
                        result[key] = int(value)
        f.close()
        return result

def read_ignore(ignore_file):
        result = []
        with open(ignore_file) as f:
                for line in f:
                        line=line.strip()
                        if line in mnemonics:
                                result.append(mnemonics.get(line))
                        else:
                                try:
                                        result.append(int(line))
                                except:
                                        print('ignore file error')
        f.close()
        return result

def charfilter(s):
        r=''
        for c in s:
                if ord(c)<65536:
                        r+=c
                else: #sometimes -FC00, need fix: e.g. D83DDB52 -> D83CDF52
                        r+='vk.com/images/emoji/'+hex(ord(c)+3627804672).upper()[2:]+'_2x.png'
        return r

def prints(s):
        #print(s)
        global printm
        printm+=s+'\n'

def print_attachments(attache, token):
        if attache is not None:
                for attached in attache:
                        type = attached.get('type')
                        stuff = attached.get(type)
                        if (type=='photo')or(type=='sticker'):
                                for size in photosizes:
                                        link=stuff.get('photo_'+str(size))
                                        if link is not None:
                                                prints(link)
                                                break
                        elif type=='video':
                                req = str(stuff.get('owner_id'))+'_'+str(stuff.get('id'))+'_'+str(stuff.get('access_key'))
                                prints(call_api('video.get', {'videos': req}, token).get('items')[0].get('player'))
                        elif type=='wall':
                                prints('vk.com/wall'+str(stuff.get('to_id'))+'_'+str(stuff.get('id')))
                        elif type=='wall_reply':
                                prints('vk.com/wall'+str(stuff.get('owner_id'))+'_'+str(stuff.get('id')))

                        else:
                                url = stuff.get('url')
                                if url is not None:
                                        urlf = url.find('?extra')        
                                        prints(url[:urlf]) if (urlf!=-1) else prints(url)
                                else:
                                        prints(type)

def getHistory(N, offset, uid, token):
        history = call_api('messages.getHistory', {'count': N, 'offset': offset, 'user_id': uid}, token).get('items')
        if history is not None:
                for message in reversed(history):
                        prints(charfilter(message.get('body')))
                        print_attachments(message.get('attachments'), token)
                        fwd = message.get('fwd_messages')
                        if fwd is not None:
                                prints('fwd_messages')
                                for fwdm in fwd:
                                        prints(str(fwdm.get('user_id'))+'#'+charfilter(fwdm.get('body')))
                                        print_attachments(fwdm.get('attachments'), token) 

def messaging():
        global token_num, printm
        print('messaging, token is', token_num)
        while True:
                m = ''
                s = ''
                userid = 0
                while (s=='')or((s[-1]!='#')and(s[-1]!='№')):
                        s=input()
                        if (m==''):
                                if (s==''): return(0)
                                attachments=None
                                if s.isdigit():
                                        ints = int(s)
                                        if ints<10: token_num = ints
                                        else: waitTime = ints
                                        continue
                                if (len(s)==1):
                                        if (s=="'")or(s=='э'):
                                                return(-1)
                                        if s=='+':
                                                s=input()
                                                attachments=s
                                                s=input() #no continue for message
                                        elif (s.lower()=='n')or(s.lower()=='т'):
                                                call_api('notifications.markAsViewed', {}, token_list[token_num])
                                                print('Done')
                                                continue
                                        elif (s.lower()=='t')or(s.lower()=='е'):
                                                s=input()
                                                lit = ast.literal_eval(s)+(token_list[token_num],)
                                                g=call_api(*lit)
                                                print(charfilter(str(g)))
                                                continue
                                        elif (s.lower()=='l')or(s.lower()=='д'):
                                                liketype, what = input().split()
                                                lowner, lid = what.split('_') #ifLiked - likes.delete
                                                print(call_api('likes.add', {'type': liketype, 'owner_id': lowner, 'item_id': lid}, token_list[token_num]))
                                        elif (s.lower()=='v')or(s.lower()=='м'):
                                                s=input()
                                                v = call_api('video.search', {'q':s, 'sort': '10', 'hd': '1', 'filters': 'long'}, token_list[token_num])
                                                for vid in v.get('items'):
                                                        print(vid.get('player'))
                                                continue
                                        elif (s=='A')or(s=='Ф'):
                                                autor=input().lower()
                                                auname=input().lower()
                                                audio_list = call_api('audio.search', {'q': autor+' '+auname}, token_list[token_num]).get('items')
                                                for audio in audio_list:
                                                        if (audio.get('artist').lower()==autor)and(audio.get('title').lower()==auname):
                                                                url = audio.get('url')
                                                                print(url[:url.find('?extra')], 'audio'+str(audio.get('owner_id'))+'_'+str(audio.get('id'))) 
                                                continue
                                        elif (s=='a')or(s=='ф'):
                                                s=input()
                                                audio_list = call_api('audio.search', {'q': s}, token_list[token_num]).get('items')
                                                print()
                                                for audio in audio_list:
                                                        url = audio.get('url')
                                                        print(audio.get('artist'),'-',audio.get('title'))
                                                        print(url[:url.find('?extra')], 'audio'+str(audio.get('owner_id'))+'_'+str(audio.get('id'))) 
                                                continue
                                        elif (s.lower()=='u')or(s.lower()=='г'):
                                                s=input()
                                                suserid = mnemonics.get(s)
                                                if suserid is None:
                                                        try:
                                                                suserid = int(s)
                                                        except:
                                                                suserid = s
                                                print(call_api('users.get', {'user_ids': suserid}, token_list[token_num]))
                                                continue
                                        elif (s.lower()=='f')or(s.lower()=='а'):
                                                s=input()
                                                suserid = mnemonics.get(s)
                                                if suserid is None: suserid = int(s)
                                                print(call_api('friends.add', {'user_id': suserid}, token_list[token_num]))
                                                continue
                                        else:
                                                print('incorrect symbol')
                                                continue
                        sharp = s.find('#')
                        Nsign = s.find('№')
                        if (Nsign>=0)and((Nsign<sharp)or(sharp<0)): sharp = Nsign
                        if userid==0:
                                try:
                                        userstr = s[:sharp]
                                        s = s[sharp+1:]
                                        userid = mnemonics.get(userstr)
                                        if userid is None: userid = int(userstr)
                                except:
                                        print('message format: userid#multiple lines message#')
                                        continue
                        m+='\n'+s
                m=m[:-1]
                if (userid==0)or(userid is None): return(0)
                if userid<0:
                         call_api('wall.post', {'owner_id': userid, 'from_group': 1, 'message': m, 'attachments': attachments}, token_list[token_num])
                if (m=='\n')and(attachments is None):
                        call_api('messages.markAsRead', {'peer_id': userid}, token_list[token_num])
                        getHistory(10, 0, userid, token_list[token_num])
                        print(printm)
                elif (m=='\n#')or(m=='\n№'):
                        getHistory(200, 0, userid, token_list[token_num])
                        print(printm)
                elif (m=='\n##')or(m=='\n№№'):
                        getHistory(200, 200, userid, token_list[token_num])
                        print(printm)        
                else:
                        call_api('messages.send', {'user_id': userid, 'message': m, 'attachment': attachments}, token_list[token_num])
                        getHistory(10, 0, userid, token_list[token_num])
                        print(printm)
                print('Done')

def check_inbox():
        A=0
        global token_num
        for index, mytoken in enumerate(token_list):
                myname = call_api('users.get', {}, mytoken)[0]
                viewed_time = call_api('notifications.get',{'count': '0'}, mytoken).get('last_viewed')
                notif_resp = call_api('notifications.get',{'start_time': viewed_time}, mytoken)
                resp = call_api('messages.getDialogs', {'unread': '1'}, mytoken)
                r = notif_resp.get('count')
                t = resp.get('count')
                A+=r+t
                prints(myname.get('first_name')+' '+myname.get('last_name')+' - '+str(t)+' new dialogues'+' - '+str(r)+' new responses')
                items = resp.get('items')
                if items:
                        for x in resp.get('items'):
                                N = x.get('unread')
                                mes = x.get('message')
                                chat_id = mes.get('chat_id')
                                if chat_id is None: #check dialogue is not a chat
                                        uid = mes.get('user_id')
                                        if uid in ignore:
                                                A-=1
                                                t-=1
                                                continue
                                        respname = call_api('users.get', {'user_ids': uid}, mytoken)[0]
                                        prints(respname.get('first_name')+' '+respname.get('last_name')+' '+str(uid)+' '+str(N)+' messages')
                                        getHistory(N, 0, uid, mytoken)
                                else:
                                        call_api('messages.markAsRead', {'peer_id': 2000000000+chat_id}, mytoken) #autoread
                                        A-=1
                                        t-=1
                if (t>0): token_num = index
                prints("-------")
                for x in reversed(notif_resp.get('items')):
                        parent = x.get('parent')
                        xtype = x.get('type')
                        if parent is None:
                                prints('no_parent')
                        else:
                                parent_id = parent.get('to_id')
                                if parent_id is None:                
                                      if parent.get('post') is not None:
                                              parent = parent.get('post')
                                              parent_id = parent.get('to_id')
                                      elif parent.get('photo') is not None:
                                              parent = parent.get('photo')
                                              parent_id = parent.get('owner_id')
                                      else:
                                              parent_id = parent.get('owner_id')
                                if 'photo' in xtype:
                                      prints('vk.com/photo'+str(parent_id)+'_'+str(parent.get('id')))
                                else:
                                      prints('vk.com/wall'+str(parent_id)+'_'+str(parent.get('id')))
                        feedback = x.get('feedback')
                        whos = feedback.get('items')
                        if whos is not None:
                                for who in whos:
                                        whuid = who.get('from_id')
                                        whuidinfo = call_api('users.get', {'user_ids': whuid}, mytoken)[0]
                                        prints(whuidinfo.get('first_name')+' '+whuidinfo.get('last_name')+' '+str(whuid))
                        comment = feedback.get('text')
                        if comment is None:
                                prints(xtype)
                        else:
                                prints(charfilter(comment))
                                print_attachments(feedback.get('attachments'), mytoken)
                prints("_____________")
        return(A) #messages+notifies of all tokens

def main():
        global printm, mnemonics, ignore, waitTime, looping
        mnemonics = read_mnemonics('mnemo.txt')
        ignore = read_ignore('ignore.txt')
        while True:
                mes=0
                mes=messaging()
                while (mes!=-1):
                        printm='\n'
                        check_inbox()
                        print(printm)
                        mes=messaging()
                else:
                        printm=''
                        looping = True
                        while (check_inbox()==0):
                                printm=''
                                print('-')
                                try:
                                        for timer in range(waitTime):
                                                time.sleep(1)
                                except KeyboardInterrupt:
                                        break
                        else:
                                master=Tk()
                                master.wm_attributes("-topmost", 1)
                                master.wm_state('normal')
                                w = Canvas(master, width=width, height=height)
                                w = Message(master, text=printm)
                                w.pack()
                                master.mainloop()
                                print(printm)
                        looping = False
if __name__ == '__main__':
        main()
