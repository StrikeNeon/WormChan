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
                    if ('{}'.format(post['tim'])+ext) not in pic_folder:
                        urllib.request.urlretrieve(image_url, pic_folder+'/{}'.format(post['tim'])+ ext)
                    else: pass
                if '.gif' in ext:
                    if ('{}'.format(post['tim'])+ext) not in gif_folder:
                        urllib.request.urlretrieve(image_url, gif_folder+'/{}'.format(post['tim'])+ ext)
                    else: pass
                if '.webm' in ext:
                    if ('{}'.format(post['tim'])+ext) not in webm_folder:
                        urllib.request.urlretrieve(image_url, webm_folder+'/{}'.format(post['tim'])+ ext)
                    else: pass
                if '.swf' in ext:
                    if ('{}'.format(post['tim'])+ext) not in swf_folder:
                        urllib.request.urlretrieve(image_url, swf_folder+'/{}'.format(post['tim'])+ ext)
                    else: pass
                if '.pdf' in ext:
                    if ('{}'.format(post['tim'])+ext) not in pdf_folder:
                        urllib.request.urlretrieve(image_url, pdf_folder+'/{}'.format(post['tim'])+ ext)
                    else: pass
                if '666' in number:
                     if ('{}'.format(number)+ext) not in SATAN_folder:
                         urllib.request.urlretrieve(image_url, SATAN_folder+'/{}'.format(number)+ ext)
                     else: pass
                 
                else:
                    pass
            except urllib.error.ContentTooShortError:
                print('urlopen error retrieval incomplete')


relevants = []


def board_task(x):
    thread = catalog_list(x)
    print(thread)
    for i in thread:
        print(i)
        try:
            get_resources(x,i)
        except urllib.error.HTTPError:
            print('missing link')
            pass
        except PermissionError:
            print('access denied')
            pass 
    print(x + 'taken')

    
def memeater():
    run = True
    while run:
        if len(relevants)>1:
            t0 = threading.Thread(target = board_task, args = (relevants.pop(-1),))
            t1 = threading.Thread(target = board_task, args = (relevants.pop(-1),))
            t0.start()
            t1.start()
            t0.join()
            t1.join()
        else:
            if len(relevants) == 1:
                t2 = threading.Thread(target = board_task, args = (relevants.pop(-1),))
                t2.start()
                t2.join()
                print('mems taken')
                run = False
            else:
                print('mems taken')
                run = False
        
memeater()
