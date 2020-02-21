# -*- coding: utf-8 -*-

#start of import list
import urllib
import urllib.request
import json
import requests


import threading
import os
#end of import list

#getting program and resouce paths
scriptDIR = os.path.dirname(__file__)
pic_folder = os.path.join(scriptDIR, 'PICS')
text_folder = os.path.join(scriptDIR, 'TEXTS')
pdf_folder = os.path.join(scriptDIR, 'PDFS')
swf_folder = os.path.join(scriptDIR, 'SWF')
webm_folder = os.path.join(scriptDIR, 'WEBM')
gif_folder = os.path.join(scriptDIR, 'GIFS')
tesfolder = os.path.join(scriptDIR, 'test')
SATAN_folder = os.path.join(scriptDIR, '666')

#------------------------------------------------------------------------------
#Working code below
#------------------------------------------------------------------------------

def catalog_list(boardNAME):
    url = 'http://a.4cdn.org'+boardNAME+'catalog.json'
    responce = requests.get(url)
    threads = []
    if responce:
        output = responce.json()
        for page in output:
            for thread in page['threads']:
                try:
                    threads.append(str(thread['no']))
                except KeyError:
                    continue
    return threads

def get_thread(boardNAME,thread):
    url = 'http://a.4cdn.org'+boardNAME+'thread/'+thread+'.json'
    response = urllib.request.urlopen(url)
    output = response.read().decode('utf-8')
    if output:
        # Parse for success or failure
        out = json.loads(output)
        for post in out['posts']:
            try:
                print(thread['sub'])
                print(post['com'])
                print("-------------------------------------")
            except KeyError:
                    continue

def get_resources(boardNAME,thread):
    url = 'http://a.4cdn.org/'+boardNAME+'/thread/'+thread+'.json'
    response = urllib.request.urlopen(url)
    output = response.read().decode('utf-8')
    if output:
        # Parse for success or failure
        out = json.loads(output)
        for post in out['posts']:
            try:
                tim = str(post['tim'])
                ext = str(post['ext'])
                number = str(post['no'])
            except KeyError:
                continue
            image_url = 'http://i.4cdn.org' + boardNAME+'' + tim + ext
            print(image_url)
            try:
                if '.jpg' or '.png' in ext:
                    urllib.request.urlretrieve(image_url, pic_folder+'/{}'.format(post['tim'])+ ext)
                elif '.gif' in ext:
                    urllib.request.urlretrieve(image_url, gif_folder+'/{}'.format(post['tim'])+ ext)
                elif '.webm' in ext:
                    urllib.request.urlretrieve(image_url, webm_folder+'/{}'.format(post['tim'])+ ext)
                elif '.swf' in ext:
                    urllib.request.urlretrieve(image_url, swf_folder+'/{}'.format(post['tim'])+ ext)
                elif '.pdf' in ext:
                    urllib.request.urlretrieve(image_url, pdf_folder+'/{}'.format(post['tim'])+ ext)
                elif '666' in number:
                    urllib.request.urlretrieve(image_url, SATAN_folder+'/{}'.format(number)+ ext)
                else:
                    pass
            except urllib.error.ContentTooShortError:
                print('urlopen error retrieval incomplete')

#relevants = ['/sci/','/mu/', '/x/', '/k/', '/m/', '/g/', '/tg/' '/s4s/','/bant/']  
#relevants = ['/sci/', '/x/', '/g/', '/tg/' '/s4s/','/bant/'] 
relevants = [ '/sci/', '/x/', '/g/','/tg/','/s4s/','/bant/']
def thread_task(x):
    print('taking '+ relevants[x])
    thread = catalog_list(relevants[x])
    print(thread)
    for i in thread:
        print(i)
        get_resources(relevants[x],i)
    print(relevants[x]+ ' taken')
      
    
def memeater():
    if len(relevants)%2==0:
        for i in range (0, len(relevants), 2):
            t0 = threading.Thread(target = thread_task, args = (i,))
            t1 = threading.Thread(target = thread_task, args = (i+1,))
        
            t0.start()
            t1.start()
        
            t0.join()
            t1.join()
        


        print('mems taken')
        
memeater()