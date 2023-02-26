import re
import asyncio
import time

#run pip install -r requirements.txt to install these if you don't already have them
import requests
import websockets
import pandas as pd

from concurrent.futures import ThreadPoolExecutor 
executor=ThreadPoolExecutor(max_workers=1)
LOCDICT,PREFIXES,LENGTH={},('cs_','qs_'),3000


CUR='BITSTAMP:BTCUSD'
# change this to any exchange.On a chart in the website scrape the link on the search bar like, for example this link ->
#     https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT
#     CUR='BINANCE:BTCUSD'

class common_:
    def format_messages(update=None):
        global LENGTH
        time_dict={'1_minute':'1', '3_minutes':'3','5_minutes':'5', '15_minutes':'15',\
                    '30_minutes':'30', '45_minutes':'45',   '1_hour':'1H','2_hours':'2H',\
                    '3_hours':'3H','4_hours':'4H','1_day':'1D','1_week':'1W','1_month':'1M'}
        if update:
            for i,j in time_dict.items():
                print('Enter',j+' '*5+'for  '+i)
            _=input()
            if _ not in time_dict.values():
                raise Exception(f'{_} not in {tuple(time_dict.values())}')
            length=int(input(f'how many bars of {[k for k, v in time_dict.items() if v == _][0]}? >100 & <10000 '))
            length=length if length>100 and length<10000 else 300
            time_dict=_
            LENGTH=length        
        else:
            time_dict='1'
            length=LENGTH

        msg=[
            '~m~526~m~{"m":"set_auth_token","p":["unauthorized_user_token"]}',
            '~m~55~m~{"m":"chart_create_session","p":["cs_XROjl1FK6WNG",""]}',
            '~m~52~m~{"m":"quote_create_session","p":["qs_bXWAHuxCI6G5"]}',
            f'~m~153~m~{{"m":"quote_add_symbols","p":["qs_bXWAHuxCI6G5","={{\\"adjustment\\":\\"splits\\",\\"currency-id\\":\\"USD\\",\\"session\\":\\"regular\\",\\"symbol\\":\\"{CUR}\\"}}"]}}',
            f'~m~162~m~{{"m":"resolve_symbol","p":["cs_XROjl1FK6WNG","sds_sym_1","={{\\"adjustment\\":\\"splits\\",\\"currency-id\\":\\"USD\\",\\"session\\":\\"regular\\",\\"symbol\\":\\"{CUR}\\"}}"]}}',
            '~m~64~m~{"m":"switch_timezone","p":["cs_XROjl1FK6WNG","Africa/Nairobi"]}',
            f'~m~81~m~{{"m":"create_series","p":["cs_XROjl1FK6WNG","sds_1","s1","sds_sym_1","{time_dict}",{length},""]}}',
            '~m~432~m~{"m":"quote_set_fields","p":["qs_bXWAHuxCI6G5","base-currency-logoid","ch","chp","currency-logoid","currency_code","currency_id","base_currency_id","current_session","description","exchange","format","fractional","is_tradable","language","local_description","listed_exchange","logoid","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","typespecs","update_mode","volume","value_unit_id"]}',
            f'~m~154~m~{{"m":"quote_fast_symbols","p":["qs_bXWAHuxCI6G5","={{\\"adjustment\\":\\"splits\\",\\"currency-id\\":\\"USD\\",\\"session\\":\\"regular\\",\\"symbol\\":\\"{CUR}\\"}}"]}}',
            '~m~65~m~{"m":"request_more_tickmarks","p":["cs_XROjl1FK6WNG","sds_1",10]}',
            '~m~60~m~{"m":"request_more_data","p":["cs_XROjl1FK6WNG","sds_1",28]}',
            f'~m~61~m~{{"m":"quote_add_symbols","p":["qs_bXWAHuxCI6G5","{CUR}"]}}',
            f'~m~166~m~{{"m":"quote_fast_symbols","p":["qs_bXWAHuxCI6G5","={{\\"adjustment\\":\\"splits\\",\\"currency-id\\":\\"USD\\",\\"session\\":\\"regular\\",\\"symbol\\":\\"{CUR}\\"}}","{CUR}"]}}'
        ]
        return msg

    def format_ws_msgs(specify):
        '''Adds the length of the message between some prefix'''
        msg=common_.format_messages(specify)
        msg=map(common_.parse_ws_message,msg)
        try:
            msg=tuple(map(lambda msg: f'~m~{len(msg[msg.find("~{") + 1:])}~m~{msg[msg.find("~{") + 1:]}',msg))
            return msg
        except AttributeError:
            return None
        
    def get_auth_token():
        '''make sure the username and password matches.
        however,you may uncomment line 98 and comment line 97 not to signin'.
        The server will send messages to the websocket still, but for a limited time or none.
        '''
        username,password=(input(f'{i} ') for i in ('username','password'))
        data = {"username":{username},"password":{password},"remember": "off"}
        try:
            _=requests.post(url='https://www.tradingview.com/accounts/signin/', data=data, headers={'Referer': 'https://www.tradingview.com'}).json()['user']['auth_token']
            return _
        except requests.exceptions.ConnectionError as e:
            print(e)
        except KeyError as e:
            if 'user' in str(e):print('wrong password or username')
            return None

    def __12_rand__(prefix):
        '''generates prefix+random 12-character string'''
        from string import ascii_lowercase as letters
        from random import choice
        random_string = ''.join(choice(letters) for i in range(12))
        return prefix+random_string

    def parse_ws_message(msg):
        '''parses the message and adds the random character generated by __12_rand__().It also adds auth key'''
        loc1=[re.search(f'{_}.+?"',msg) for _ in PREFIXES ]
        if loc1[0] and loc1[1] is not None or loc1[0] ==loc1[1]:
            auth_token=common_.get_auth_token()
            if auth_token is None:
                return None
            return msg.replace('unauthorized_user_token',auth_token)
            # return msg
        match,prefix=(loc1[0],PREFIXES[0]) if loc1[0] is not None else (loc1[1],PREFIXES[1])
        span=match.span()
        match=match.group(0)[:-1]
        if match in LOCDICT.values():
            key=[k for k, v in LOCDICT.items() if v == match][0]
        else:
            LOCDICT[key:=common_.__12_rand__(prefix)]=match
        if len(key)==len(match):
            msg=msg.replace(match,key)
        elif 'snapshoter' in match:
            msg=msg.replace(msg[span[1]-14:span[1]-1],key[2:])
        else:
            raise Exception(f'length of common session random in {msg} does not match')
        return msg
    
    def queue_get_block(queue):
        '''getting message from async queue without blocking it'''
        while 1:
            try:
                return queue.get_nowait()
            except asyncio.queues.QueueEmpty:
                time.sleep(1)

    def __send__(msg,S):
        S.send(msg)
        if not S.recv():
            S.close()
            return 1

    def format_text(queue,S,session_rand):
        ''' formatting messages from the queue and send them to a socket S.'''
        global LENGTH
        ptrn='"v":\[((.+?,){5})'
        try:
            _=common_.queue_get_block(queue)
            g_list= re.search('","s":\[(.+?)\],"?',_).group(1).split('},{')
            for i in range (len(g_list)):
                g_list[i]=re.search(ptrn,g_list[i]).group(1).rstrip(',').split(',')
            if common_.__send__(g_list,S):return
            while 1:
                msg=common_.queue_get_block(queue)
                msg=msg.split('~m~{"m":"du",')
                _=f'"p":["{session_rand}",{{"sds_1":{{"s":[{{"i":{LENGTH}'
                for i in msg:
                    if _ in i:
                        g_list=[re.search(ptrn,i).group(1).split(',')[:-1]]
                        LENGTH+=1
                        if  common_.__send__(g_list,S):return
                        break
        except AttributeError as e:
            print(ptrn,_,'\n',e)
            from sys import exit
            exit()

class Tview_wsmsgs:
    '''Trading_View websocket messages'''
    def __init__(self,S,specify=False):
        self.msg_queue=asyncio.Queue(maxsize=1)
        self.start(S,specify)

    def start(self,S,specify):        
        self.msg=common_.format_ws_msgs(specify)
        if self.msg is None:return
        for session_rand in tuple(LOCDICT.keys()):
            if PREFIXES[0] in session_rand:
                loop=asyncio.new_event_loop()
                loop.run_until_complete(self.ws_connect(session_rand,loop,S))

    async def keep_sending(self):
        counter=1
        while 1:
            suffix=f'~h~{counter}'
            whole=f'~m~{len(suffix)}~m~'+suffix
            await asyncio.sleep(10)
            await self.ws.send(whole)
            counter+=1

    async def recv_messages(self):
        while 1:
            try:
                await self.msg_queue.put(await self.ws.recv())
            except asyncio.queues.QueueEmpty:                
                pass

    async def ws_connect(self,session_rand,loop,S):
        '''connect with websocket url and send all global messages\  
        create  taskgoup and add recv_messages() and keep_sending() coroutines'''

        '''create a sync thread to get messages from the recv_queue and start it NOW'''
        loop.run_in_executor(executor,common_.format_text,self.msg_queue,S,session_rand)
        try:
            self.ws=await websockets.connect('wss://data.tradingview.com/socket.io/websocket',extra_headers={'Origin':'https://www.tradingview.com'})
        except Exception as e:
            print(e)
            return
        '''send all messages IN ORDER and receive them.\
        put intresting message in a queue'''
        print('Switching Protocols')
        _=1
        for i in self.msg:
            await self.ws.send(i)
            msg=await self.ws.recv()
            if _:
                if '"s":[{"i":0' in msg:
                    await self.msg_queue.put(msg)
                    format_text_=0
        '''creates two tasks:
                1.recv_messages() reveives messages and put them in a queue
                2.send messages() sends messages after 10 seconds
        '''
        t1=asyncio.create_task(self.recv_messages())
        t2=asyncio.create_task(self.keep_sending())
        await t1,t2

if __name__=='__main__':
    pass
    
