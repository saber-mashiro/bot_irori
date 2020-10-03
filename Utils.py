import os
import requests
import asyncio
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import traceback
import random
import string
import functools
import GLOBAL
import json
from typing import *
from PIL import Image as PImage
from PIL import ImageFont,ImageDraw
import base64
import importlib
import sys
# from mirai.face import QQFaces
# from mirai import Mirai, Plain, MessageChain, Friend, Face, MessageChain, Group, Image, Member, At, Source

# from graia.application import GraiaMiraiApplication as Mirai
# from graia.application import Session
# from graia.application.event.messages import FriendMessage,GroupMessage
# from graia.application.event.lifecycle import ApplicationLaunched,ApplicationShutdowned
# from graia.application.message.chain import MessageChain
# from graia.application.message.elements.internal import Plain, Image, At, Face, Source
# from graia.broadcast import Broadcast
# from graia.application.group import Group,Member
# from graia.application.friend import Friend

def importMirai():
    global Mirai, Session, FriendMessage, GroupMessage, ApplicationLaunched, ApplicationShutdowned
    global MessageChain, Plain, Image, At, Face, Source, Broadcast, Group, Member, Friend, QQFaces
    try:
        if GLOBAL.py_mirai_version == 3:raise ImportError
        Mirai = getattr(importlib.import_module("graia.application"),"GraiaMiraiApplication")
        Session = getattr(importlib.import_module("graia.application"),"Session")
        FriendMessage = getattr(importlib.import_module("graia.application.event.messages"),"FriendMessage")
        GroupMessage = getattr(importlib.import_module("graia.application.event.messages"),"GroupMessage")
        ApplicationLaunched = getattr(importlib.import_module("graia.application.event.lifecycle"),"ApplicationLaunched")
        ApplicationShutdowned = getattr(importlib.import_module("graia.application.event.lifecycle"),"ApplicationShutdowned")
        MessageChain = getattr(importlib.import_module("graia.application.message.chain"),"MessageChain")
        Plain = getattr(importlib.import_module("graia.application.message.elements.internal"),"Plain")
        Image = getattr(importlib.import_module("graia.application.message.elements.internal"),"Image")
        At = getattr(importlib.import_module("graia.application.message.elements.internal"),"At")
        Face = getattr(importlib.import_module("graia.application.message.elements.internal"),"Face")
        Source = getattr(importlib.import_module("graia.application.message.elements.internal"),"Source")
        Broadcast = getattr(importlib.import_module("graia.broadcast"),"Broadcast")
        Group = getattr(importlib.import_module("graia.application.group"),"Group")
        Member = getattr(importlib.import_module("graia.application.group"),"Member")
        Friend = getattr(importlib.import_module("graia.application.friend"),"Friend")
        GLOBAL.py_mirai_version = 4
    except ImportError:
        Mirai = getattr(importlib.import_module("mirai"),"Mirai")
        Plain = getattr(importlib.import_module("mirai"),"Plain")
        MessageChain = getattr(importlib.import_module("mirai"),"MessageChain")
        Friend = getattr(importlib.import_module("mirai"),"Friend")
        Face = getattr(importlib.import_module("mirai"),"Face")
        MessageChain = getattr(importlib.import_module("mirai"),"MessageChain")
        Group = getattr(importlib.import_module("mirai"),"Group")
        Image = getattr(importlib.import_module("mirai"),"Image")
        Member = getattr(importlib.import_module("mirai"),"Member")
        At = getattr(importlib.import_module("mirai"),"At")
        Source = getattr(importlib.import_module("mirai"),"Source")
        QQFaces = getattr(importlib.import_module("GLOBAL"),"QQFaces")
        GLOBAL.py_mirai_version = 3

importMirai()

youbi = {
    1:'月曜日',
    2:'火曜日',
    3:'水曜日',
    4:'木曜日',
    5:'金曜日',
    6:'土曜日',
    7:'日曜日',
}

from GLOBAL import SessionConfigures
def chkcfg(player):return GLOBAL.cfgs.setdefault(player,SessionConfigures(player))

def getPlainText(p:Plain):
    """做v3和v4的Plain兼容"""
    if GLOBAL.py_mirai_version == 3: return p.toString()
    else: return p.asDisplay()

def getMessageChainText(m:MessageChain):
    """做v3和v4的MessageChain兼容"""
    if GLOBAL.py_mirai_version == 3: return m.toString()
    else: return m.asDisplay()

async def WeatherSubscribeRoutiner():
    print('进入回环(天气预报')
    if not os.path.exists('weather/'):
        os.mkdir('weather/')
    while 1:

        print(f'weather report waiting for {86400+5-(datetime.datetime.now().timestamp()+8*3600)%86400}')
        await asyncio.sleep(86400+5-(datetime.datetime.now().timestamp()+8*3600)%86400)

        for _ in os.listdir('weather/'):
            try:
                with open('weather/'+_,'r') as f:
                    dt = datetime.datetime.now()
                    ans = [f'今天是{dt.year}年{dt.month}月{dt.day}日，{youbi[dt.isoweekday()]}']

                    try:
                        bs = BeautifulSoup(requests.get('https://wannianrili.51240.com/').text,'html.parser')
                        res = bs('div',attrs={'id':'jie_guo'})
                        ans.append('农历'+res[0].contents[0].contents[dt.day]('div',attrs={'class':"wnrl_k_you_id_wnrl_nongli"})[0].string)
                        ans.append(res[0].contents[dt.day]('span',string='节气')[0].nextSibling.string)
                    except:
                        ans.append('我忘了今天农历几号了')
                        print(traceback.format_exc())

                    if random.randint(0,3):
                        ans.append(random.choice(['还在盯着屏幕吗？','还不睡？等死吧','别摸了别摸了快点上床吧','白天再说.jpg','邀请你同床竞技']))

                    for city in f.readlines():
                        if city.strip():
                            j = fetchWeather(city.strip())
                            ans += j[:3]
                asyncio.ensure_future(msgDistributer(msg='\n'.join(ans),typ='P',player=_))

            except:
                print('天气预报姬挂了！',traceback.format_exc())

async def SentenceSubscribeRoutiner():
    print('进入回环(每日一句')
    if not os.path.exists('sentence/'):
        os.mkdir('sentence/')
    while 1:

        print(f'sentence report waiting for {86400+5-(datetime.datetime.now().timestamp()+15*3600)%86400}')
        await asyncio.sleep(86400+5-(datetime.datetime.now().timestamp()+15*3600)%86400)

        for _ in os.listdir('sentence/'):
            try:
                d={}
                fetchSentences(d)
                if 'img' in d:
                    asyncio.ensure_future(msgDistributer(msg=d['img'],typ='I',player=_))
                asyncio.ensure_future(msgDistributer(msg='\n'.join(d['plain']),typ='P',player=_))

            except:
                print('每日一句挂了！',traceback.format_exc())

async def CFLoopRoutiner():
    print('进入回环(CF')
    if not os.path.exists('CF/'):
        os.mkdir('CF/')
    while 1:
        if any([_ for _ in os.listdir('CF/') if _[-4:]!='.png']):
            j = fetchCodeForcesContests()
            for _ in os.listdir('CF/'):
                try:
                    if _[-4:]!='.png':
                        CFNoticeManager(j,gp=int(_))
                except:
                    print('CF爬虫挂了！',traceback.format_exc())
        await asyncio.sleep(86400)

async def ATLoopRoutiner():
    print('进入回环(AT')
    if not os.path.exists('AtCoder/'):
        os.mkdir('AtCoder/')
    while 1:
        if any([_ for _ in os.listdir('AtCoder/') if _[-4:]!='.png']):
            j = fetchAtCoderContests()
            for _ in os.listdir('AtCoder/'):
                try:
                    if _[-4:]!='.png':
                        OTNoticeManager(j['upcoming'],gp=int(_))
                except:
                    print('AT爬虫挂了！',traceback.format_exc())
        await asyncio.sleep(86400)

async def NCLoopRoutiner():
    print('进入回环(NC')
    if not os.path.exists('NowCoder/'):
        os.mkdir('NowCoder/')
    while 1:
        if any([_ for _ in os.listdir('NowCoder/') if _[-4:]!='.png']):
            j = fetchNowCoderContests()
            for _ in os.listdir('NowCoder/'):
                try:
                    if _[-4:]!='.png':
                        OTNoticeManager(j,gp=int(_))
                except:
                    print('NC爬虫挂了！',traceback.format_exc())
        await asyncio.sleep(86400)

async def rmTmpFile(fi:str):
    await asyncio.sleep(60)
    os.remove(fi)

async def contestsBeginNotice(g,contest,ti):
    if ti<0:
        return
    print('进入等待队列，阻塞%f秒'%ti)
    await asyncio.sleep(ti)
    await msgDistributer(gp=g,msg=f'比赛{contest}还有不到一个小时就要开始了...')

async def CFProblemRender(g,cid,ti):
    FN='CF/%s.png' % cid
    print('在%f秒后渲染比赛'%ti+cid+'的问题图片')
    if cid in GLOBAL.CFRenderFlag or os.path.exists(FN): #有队列在做了
        await asyncio.sleep(ti)
        if not os.path.exists(FN):
            await asyncio.sleep(20)
        await msgDistributer(gp=g,msg=FN,typ='I')
    else:
        GLOBAL.CFRenderFlag.add(cid)
        await asyncio.sleep(ti)
        base = 'https://codeforces.com/contest/'+cid+'/problems'
        l = renderHtml(base,FN)
        GLOBAL.CFRenderFlag.discard(ti)
        l.append(Image.fromFileSystem(FN))
        await msgDistributer(gp=g,list=l)

async def fuzzT(g,s,e,w=''):
    for _ in range(s,e):
        if _%10==0:
            await asyncio.sleep(0.2)
        await msgDistributer(gp=g,msg=f'{chr(_)}{_}{w}')


async def msgDistributer(**kwargs):
    """
    根据player号分发消息
    输入字典msg为源文本，typ标识其类型('E'表情,'I'图片文件目录,'P'普通文本)
    扩展了也可以扔消息元素列表(list)进来的功能
    """
    seq = []
    
    if 'msg' in kwargs and kwargs['msg']:
        if kwargs.get('typ','P') == 'E':
            seq = [Face(QQFaces[kwargs['msg']])]
        elif kwargs.get('typ','P') == 'I':
            # print(base64.b64decode(kwargs['msg']))
            try: # 这个try用来判断msg是不是可解码的b64
                base64.b64decode(kwargs['msg'])
                f_n = 'tmp'+randstr(8)
                with open(f_n,'wb') as f:
                    f.write(base64.b64decode(kwargs['msg']))
                asyncio.ensure_future(rmTmpFile(f_n))
                seq = [Image.fromFileSystem(f_n)]
                # seq = [Image.fromFileSystem(kwargs['msg'])]
            except:
                if kwargs['msg'][:4] == 'http':
                    r = requests.get(kwargs['msg'])
                    f_n = 'tmp'+randstr(8)
                    with open(f_n,'wb') as f:
                        f.write(r.content)
                    asyncio.ensure_future(rmTmpFile(f_n))
                    seq = [Image.fromFileSystem(f_n)]
                else:
                    seq = [Image.fromFileSystem(kwargs['msg'])]
        else:
            seq = [Plain(kwargs['msg'])]

    if 'list' in kwargs and kwargs['list']:
        seq += kwargs['list']

    if seq:
        if 'player' in kwargs:
            kwargs['player'] = int(kwargs['player'])
            if kwargs['player'] > 1<<39:
                await GLOBAL.app.sendGroupMessage(kwargs['player']-(1<<39),compressMsg(seq))
            else:
                await GLOBAL.app.sendFriendMessage(kwargs['player'],compressMsg(seq))
        elif 'gp' in kwargs:
            await GLOBAL.app.sendGroupMessage(kwargs['gp'],compressMsg(seq))
        elif 'mem' in kwargs:
            await GLOBAL.app.sendFriendMessage(kwargs['mem'],compressMsg(seq))
        

def tnow():return datetime.datetime.utcnow() + datetime.timedelta(hours=8)

def randstr(l:int) -> str:return ''.join(random.sample(string.ascii_letters*l+string.digits*l,l))

def renderHtml(dst_lnk,na) -> str:
    """渲染dst_lnk的网页，保存为na，返回网页标题"""
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-gpu')
    option.add_argument("--window-size=1280,1024")
    option.add_argument("--hide-scrollbars")
    
    driver = webdriver.Chrome(options=option)
    
    driver.get(dst_lnk)
    ostr = []
    ostr.append(Plain(text=driver.title))
    location = driver.execute_script('return window.location.href')
    ostr.append(Plain(text=location))
    
    scroll_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    scroll_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    if scroll_height*scroll_width > GLOBAL.webPngLimit:
        if scroll_width >= GLOBAL.webPngLimit:
            driver.quit()
            ostr.append(Plain(text='我画不了这么鬼畜的页面OxO'))
            return ostr
        else:
            if 'codeforces' in dst_lnk:
                scroll_height = min(GLOBAL.webPngLimit*10//scroll_width,scroll_height)
            else:
                scroll_height = GLOBAL.webPngLimit//scroll_width
    if 'moegirl' in dst_lnk:
        driver.execute_script('''var o=document.querySelectorAll('.heimu');for(var i=0;i<o.length;i++){o[i].style.color="#FFF"}''')
        driver.execute_script('''var o=document.querySelectorAll('a');for(var i=0;i<o.length;i++){o[i].style.color="#0AF"}''')
    driver.set_window_size(scroll_width, scroll_height)
    driver.get_screenshot_as_file(na)
    driver.quit()
    return ostr

def generateTmpFileName(pref,ext='.png',**kwargs):
    return f'''tmp{pref}{randstr(GLOBAL.randomStrLength)}{ext}'''

def compressMsg(l,extDict={}):
    """会把Plain对象展开，但同时也会打乱由图片，文字，回复等成分组成的混合消息链"""
    player = extDict.get("player",0)
    tc = chkcfg(player)
    theme = int(extDict.get("-theme",255))
    offset = tc.font_size >> 1
    print(offset)
    nl = []
    others = []
    for i in l:
        if isinstance(i,Plain):
            nl.append(getPlainText(i))
        else:
            others.append(i)
    print(others)
    s = ''.join(nl)
    if len(s) >tc.compress_threshold or "-force-image" in extDict:
        
        font = ImageFont.truetype('sarasa-gothic-ttf-0.12.5/sarasa-ui-tc-bold.ttf',GLOBAL.compressFontSize)
        
        sl = s.split('\n')
        height = len(sl)
        width = 0
        for i in sl:
            width = max(width,len(i))

        layer2 = PImage.new(
            'RGBA',
            (width * (GLOBAL.compressFontSize), (height) * (GLOBAL.compressFontSize +offset)),
            (255 - theme, 255 - theme, 255 - theme, 255)
        )
        p = generateTmpFileName('ZIP')
        # PImage.alpha_composite(nyaSrc,layer2).save(p)
        draw = ImageDraw.Draw(layer2)

        for column,txt in enumerate(sl):
            draw.text((offset>>1,   column * ((offset)+GLOBAL.compressFontSize)), txt, (theme,theme,theme,255), font)
        layer2.save(p)
        asyncio.ensure_future(rmTmpFile(p))
        l = [Image.fromFileSystem(p)] + others

    if GLOBAL.py_mirai_version == 3:
        return l
    else:
        return MessageChain.create(l).asSendable()

def getPlayer(**kwargs):
    if 'gp' in kwargs:
        try:
            player = kwargs['gp'].id + 2**39
        except:
            player = kwargs['gp'] + 2**39
    else:
        try:
            player = kwargs['mem'].id
        except:
            player = kwargs['mem']
    return player

def removeSniffer(player,event):
    print(chkcfg(player).quick_calls.pop(event,"?"))
    try:
        with open(f'sniffer/{player}','r') as f:
            j = json.load(f)
        del j[event]
        with open(f'sniffer/{player}','w') as f:
            json.dump(j,f)
    except:
        print('缓存sniffer文件出错')
        print(traceback.format_exc())

def overwriteSniffer(player,event,pattern,*attrs):
    eventObj = {event:{'sniff':[pattern],'attrs':attrs}}
    chkcfg(player).quick_calls.update(eventObj)
    if not os.path.exists(f'sniffer/{player}'):
        with open(f'sniffer/{player}','w') as f:
            json.dump(eventObj,f)
        return
    with open(f'sniffer/{player}','r') as f:
        j = json.load(f)
    j.update(eventObj)
    with open(f'sniffer/{player}','w') as f:
        json.dump(j,f)

def appendSniffer(player,event,pattern): # 注意捕捉exc
    chkcfg(player).quick_calls[event]['sniff'].append(pattern)
    with open(f'sniffer/{player}','r') as f:
        j = json.load(f)
    j[event]['sniff'].append(pattern)
    with open(f'sniffer/{player}','w') as f:
        json.dump(j,f)

def clearCFFuture(G,key,src):
    CFNoticeQueue = GLOBAL.CFNoticeQueueGlobal.setdefault(src,{})
    try:
        print('清除成功',CFNoticeQueue.pop(key))
    except:
        print('无',G)

def clearOTFuture(G,key,src):

    t = GLOBAL.OTNoticeQueueGlobal.setdefault(src,{})
    try:
        print('清除成功',t.pop(key))
    except:
        print('无',G)

def CFNoticeManager(j,**kwargs):
    try:
        gp = kwargs['gp'].id
    except:
        gp = kwargs['gp']
    fn = f"CF/{gp}"
    with open(fn,'r') as f:
        feat = f.readline().strip()
    CFNoticeQueue = GLOBAL.CFNoticeQueueGlobal.setdefault(gp,{})
    print(j)
    for k,v in j.items():
        timew = None
        if k not in CFNoticeQueue:
            
            if 'routine' in v:
                timew = v['routine'] - tnow() - datetime.timedelta(hours=1)
                asy = asyncio.ensure_future(contestsBeginNotice(gp,v['title'],timew.total_seconds()))
                CFNoticeQueue[k] = asy
                asy.add_done_callback(functools.partial(clearCFFuture,k,gp))
        if timew and feat == 'R' and k + 'RDR' not in CFNoticeQueue:
            asyR = asyncio.ensure_future(CFProblemRender(gp,k,timew.total_seconds()+3640))
            CFNoticeQueue[k + 'RDR']=asyR
            asyR.add_done_callback(functools.partial(clearCFFuture,k + 'RDR',gp))
        elif feat == 'Y' and k + 'RDR' in CFNoticeQueue:
            t = CFNoticeQueue.pop(k + 'RDR')
            t.cancel()

def OTNoticeManager(j,**kwargs):
    try:
        gp = kwargs['gp'].id
    except:
        gp = kwargs['gp']

    OtherOJNoticeQueue = GLOBAL.OTNoticeQueueGlobal.setdefault(gp,{})

    for k in j:
        if k['title'] not in OtherOJNoticeQueue:
            timew = k['begin'] - tnow() - datetime.timedelta(hours=1)
            asy = asyncio.ensure_future(contestsBeginNotice(gp,k['title'],timew.total_seconds()))
            OtherOJNoticeQueue[k['title']] = asy
            asy.add_done_callback(functools.partial(clearOTFuture,k['title'],gp))
    print(OtherOJNoticeQueue)

def fetchCodeForcesContests():
    r = requests.get('https://codeforces.com/contests?complete=true')
    print(r)
    soup = BeautifulSoup(r.text,'html.parser')
    li = {}
    for i in soup('table')[0]('tr'):

        if any(i('td')): #标题 作者 日期 时长 开始倒计时 （爬到的是UTC+3
            contest = li.setdefault(i['data-contestid'],{})
            
            pos = i('td')[0].text.find('Enter')
            if pos!=-1:
                print('正在运行的比赛')
                contest['title'] = i('td')[0].text[:pos-1].strip()
            else:
                try:
                    contest['title'] = i('td')[0].string.strip()
                    contest['authors'] = [au.string.strip() for au in i('td')[1]('a')]
                    contest['routine'] = datetime.datetime.strptime(i('td')[2].a.span.string.strip(),'%b/%d/%Y %H:%M') + datetime.timedelta(hours=5)
                    contest['length'] = i('td')[3].string.strip()
                    contest['countdown'] = i('td')[4].text.strip()
                    
                except:
                    print(traceback.format_exc())
    return li

def fetchAtCoderContests() -> dict:
    j = {}
    l = []
    r = requests.get('https://atcoder.jp/contests/',headers = GLOBAL.AtCoderHeaders)
    s = BeautifulSoup(r.text,'html.parser')
    try:
        for p,i in enumerate(s.find('h3',string='Active Contests').next_sibling.next_sibling('tr')):
            if p:
                l.append({
                'length':i('td')[2].text,
                'ranking_range':i('td')[3].text,
                'title':i('a')[1].text,
                'begin':datetime.datetime.strptime(i('a')[0].text,"%Y-%m-%d %H:%M:%S+0900") - datetime.timedelta(hours=1)
                })
    except:
        pass
    j['running'] = l
    l = []

    for p,i in enumerate(s.find('h3',string='Upcoming Contests').next_sibling.next_sibling('tr')):# 持续时间 排名区间 比赛名 比赛时间
        if p:
            l.append({
                'length':i('td')[2].text,
                'ranking_range':i('td')[3].text,
                'title':i('a')[1].text,
                'begin':datetime.datetime.strptime(i('a')[0].text,"%Y-%m-%d %H:%M:%S+0900") - datetime.timedelta(hours=1)
                })

    j['upcoming'] = l
    print(j)
    return j

def fetchNowCoderContests() -> list:
    l = []
    res = requests.get('https://ac.nowcoder.com/acm/contest/vip-index?&headNav=www')
    bs_res = BeautifulSoup(res.text,'html.parser')
    items = bs_res.find('div',class_='platform-mod js-current')
    for item in items.find_all(class_='platform-item'):
        ans = item.find(class_='platform-item-cont')
        contest_name = ans.find('a',target='_blank').text
        contest_time = ans.find('li',class_='match-time-icon').text
        li = contest_time.split('\n')
        d = datetime.datetime.strptime(li[0],"比赛时间：%Y-%m-%d %H:%M")
        l.append({
            "title":contest_name,
            "begin":d,
            "length":li[2].strip()
        })
    return l

def fetchWeather(city: str) -> list:
    search_lnk = 'http://toy1.weather.com.cn/search?cityname=' + city
    j = json.loads(requests.get(search_lnk).text[1:-1])[0]['ref'].split('~')
    output = [f'{j[2]}的天气数据:']
    weather_lnk = f'http://www.weather.com.cn/weather/{j[0]}.shtml'
    b = BeautifulSoup(requests.get(weather_lnk).content,'html.parser')

    ctr = 0
    pos = 10
    for p,i in enumerate(b('li')):
        if i.text.find('今天')!=-1:
            ctr+=1
            if ctr>=2:
                pos = p
                break


    for i in b('li')[pos:pos+7]:
        t = i('p')
        output.append(f'{i.h1.text} {t[0].text} {t[1].text.strip()} {t[2].span["title"]}{t[2].text.strip()}')
    return output

def fetchSentences(d):
    r = requests.get(f'http://sentence.iciba.com/index.php?c=dailysentence&m=getTodaySentence&_={int(datetime.datetime.now().timestamp()*1000)}')
    j = json.loads(r.text)
    try:
        rr = requests.get(j['picture'])
        fn = 'tmp' + randstr(4)
        with open(fn,'wb') as f:
            f.write(rr.content)
        d['img'] = fn
        print(fn)
        asyncio.ensure_future(rmTmpFile(fn))
    except:
        print(f'【每日一句】爬图炸了:{traceback.format_exc()}')
    d.setdefault('plain',[]).append(j['content'])
    d.setdefault('plain',[]).append(j['note'])
    

def uploadToChaoXing(fn:str) -> str:
    lnk = 'http://notice.chaoxing.com/pc/files/uploadNoticeFile'
    with open(fn,'rb') as f:
        r = requests.post(lnk,files = {'attrFile':f})
    j = json.loads(r.text)
    return j['att_file']['att_clouddisk']['downPath']

# 数论相关

def comb(n,b):
    res = 1
    b = min(b,n-b)
    for i in range(b):
        res=res*(n-i)//(i+1)
    return res

def quickpow(x,p,m = -1):
    res = 1
    if m == -1:
        while p:
            if p&1:
                res = res * x
            x = x * x
            p>>=1
    else:
        while p:
            if p&1:
                res = res * x % m
            x = x * x % m
            p>>=1
    return res

def exgcd(a,b):
    if not b:
        return 1,0
    y,x = exgcd(b,a%b)
    y -= a//b * x
    return x,y

def getinv(a,m):
    x,y = exgcd(a,m)
    return x%m
    
# 树巨结垢相关

def lowbit(x:int): return x&-x

def treearray_update(pos:int,x:int,array:list):
    while pos < len(array):
        array[pos] += x
        pos += lowbit(pos)

def treearray_getsum(pos:int,array:list) -> int:
    ans = 0
    while pos > 0:
        ans += array[pos]
        pos -= lowbit(pos)
    return ans

def calcinvs(array:list):
    d = {}
    for k,v in enumerate(sorted(array)):
        d[v] = k+1
    treearray = [0 for i in range(1+len(array))]
    invs = 0
    for i in array:
        invs += treearray_getsum(len(treearray)-1, treearray) - treearray_getsum(d[i], treearray)
        treearray_update(d[i],1,treearray)
    return invs
