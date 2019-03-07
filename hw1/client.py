import socket
import base64
import random as rand
import requests as rqst
import sys
import select
import os

###Create Connection###
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HostIP = '140.112.28.129'
#PortNum = 6667
PortNum = 6667
ClientSocket.connect((HostIP,PortNum))


###Utils###
def send_m(msg):
    ClientSocket.send(msg.encode('utf-8'))

def recv_m(length):
    return(ClientSocket.recv(length).decode('utf-8'))

def parse_recvm(msg,pvmsg):
    nick = msg.find(':')
    usr = msg.find('!')
    ip = msg.find('@')
    nick = msg[nick+1:usr]
    usr = msg[usr+1:ip]
    ip = msg[ip+1:pvmsg]
    pvmsg = msg[pvmsg:]
    target = pvmsg.find(' ')
    txt = pvmsg.find(':')
    target = pvmsg[target+1:txt].strip()
    txt = pvmsg[txt+1:].strip()
    return nick,usr,ip,target,txt

def parse_sendm(msg,target):
    return 'PRIVMSG '+target+' :'+msg+'\r\n'

def recv(NICK):
    msg = recv_m(4096)
    if msg=='':
        return -1,0,0
    pvmsg = msg.find('PRIVMSG')
    if pvmsg==-1:
        return -1,0,0
    _nick,_usr,_ip,_target,_txt = parse_recvm(msg,pvmsg)
    if _target != NICK:
        return -1,0,0
    return 1,_nick,_txt

def send(msg,nick):
    msg = parse_sendm(msg,nick)
    send_m(msg)

###CONSTANTS###
NICK = 'bot_b05902008'
USER = 'b05902008'
CHANNEL = 'CN_DEMO'
stella = ['Capricorn','Aquarius','Pisces','Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius']

send_m('NICK '+NICK+'\r\n')
send_m('USER '+USER+'\r\n')
send_m('JOIN #'+CHANNEL+'\r\n')
send_m('PRIVMSG #CN_DEMO :Hello, I am James, nice to meet you all.\r\n')


while(True):
    code,nick,txt = recv(NICK)
    if code==-1:
        continue
    if txt in stella:
        horoscope = base64.b64encode(txt.encode('utf-8')).decode('utf-8')
        msg = 'Here is your lucky token : '+horoscope
        send(msg,nick)
        continue
    if txt == '!guess':
        history = []
        ans = rand.randint(1,10)
        msg = 'Game Start! Guess a number between 1~10'
        send(msg,nick)
        print(ans)
        while True:
            code,_,txt = recv(NICK)
            if code==-1:
                continue
            try:
                txt = int(txt)
            except ValueError:
                continue
            if txt>10 or txt<1:
                msg = 'Out of range'
                send(msg,nick)
                continue
            if txt in history:
                msg = "You've tried this before =_=. "
            else:
                history.append(txt)
                msg = ''
            if txt<ans:
                msg += 'Aim higher'
                send(msg,nick)
                continue
            if txt>ans:
                msg += 'Aim lower'
                send(msg,nick)
                continue
            if txt==ans:
                msg = 'Congratulations!'
                send(msg,nick)
                break
        continue
    if txt[:6] == '!song ':
        txt = txt[6:]
        url = 'https://www.youtube.com/results?search_query='+txt
        resp = rqst.get(url)
        a = resp.text.find('<body')
        a = resp.text[a:].split('\n')
        for i in a:
            if '/watch?v=' in i:
                i = i[i.find('watch?v='):]
                i = i[:i.find('"')]
                break
        url = 'https://www.youtube.com/'+i
        send(url,nick)
    if txt == '!chat':
        os.system('clear')
        print('========'+nick+' has initiated a chat with you========')
        print('>',end = ' ')
        sys.stdout.flush()
        while True:
            if select.select([sys.stdin,],[],[],0)[0]:
                print('>',end=' ')
                sys.stdout.flush()
                a = input()
                send(a,nick)
            if select.select([ClientSocket,],[],[],0)[0]:
                code,_,txt = recv(NICK)
                if code==-1:
                    continue
                print('\r'+nick+' : '+txt)
                print('>',end=' ')
                sys.stdout.flush()
                sys.stdout.flush()
                if txt=='!bye':
                    print('========'+nick+' has left the chat room========')
                    break


ClientSocket.close()
