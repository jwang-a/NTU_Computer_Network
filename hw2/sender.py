import socket
import random as rand
import sys
import select
import signal
import time
from pwn import *
from UDPutils import *


###Utils
#def timeout():


def main():
    ###meta ip/port
    my_ip = '127.0.0.1'
    my_port = 10101
    target_ip = '127.0.0.1'
    target_port = 10102

    ###init_data
    window = 1
    thres = 16
    lastack = 0
    restart = True
    lastsent = 0

    ###initiate socket
    sock = init_srv(my_ip,my_port)

    ###Prepare data
    if len(sys.argv)<2:
        print("Please provide file")
        exit()
    data = open(sys.argv[1],'rb').read() 
    datalength = len(data)
    if datalength==0:
        print("Don't submit empty file")
        exit()
    segment_cnt = datalength//1024
    segment = []
    for i in range(segment_cnt):
        segment.append(data[i*1024:(i+1)*1024])
    if datalength%1024!=0:
        segment.append(data[segment_cnt*1024:])
    segment_cnt = len(segment)

    ###start sending

    while True:
        if restart is True:
            for i in range(lastack,lastack+window):
                if i>=segment_cnt:
                    break
                if i>=lastsent:
                    printlog('send','data','#'+str(i)+',','winSize = '+str(window))
                else:
                    printlog('resend','data','#'+str(i)+',','winSize = '+str(window))
                send_msg(sock,pack_tcp(i,None,None,segment[i]),target_ip,target_port)
                if i>lastsent:
                    lastsent = i
            starttime = time.time()*10000000
            restart = False
        if  select.select([sock,],[],[],0)[0]:
            msg = recv_msg(sock)
            ack = unpack_tcp(msg[0])
            if ack[1]==None:
                print('?')
                continue
            if ack[2]==1:
                printlog('recv','finack')
                exit()
            printlog('recv','ack','#'+str(ack[0]))
            if ack[0]==lastack:
                starttime = time.time()*10000000
                lastack+=1
                if window<thres:
                    window*=2
                else:
                    window+=1
                if lastack==segment_cnt:
                        printlog('send','fin')
                        send_msg(sock,pack_tcp(None,None,1,b''),target_ip,target_port)
                        break
                for i in range(lastsent+1,lastack+window):
                    if i>=segment_cnt:
                        break
                    printlog('send','data','#'+str(i)+',','winSize = '+str(window))
                    send_msg(sock,pack_tcp(i,None,None,segment[i]),target_ip,target_port)
                    lastsent = i
            else:
                lastack = ack[0]+1
        curtime = time.time()*10000000
        if curtime-starttime>=10000:
            thres = max(window//2,1)
            printlog('time','out,','','threshold = '+str(thres))
            window = 1
            restart = True





main()
