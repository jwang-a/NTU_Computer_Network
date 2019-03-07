import socket
import random as rand
import sys
import select
import signal
import time
from pwn import *
from UDPutils import *




def main():
    ###meta ip/port
    my_ip = '127.0.0.1'
    my_port = 10101
    target_ip = '127.0.0.1'
    target_port = 10102

    ###init_data
    window = 1
    thres = 16
    lastack = 1
    restart = True
    lastsent = 1
    startsend = 0
    timeout_fac = 15000000
    timeout_fac = 100

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
    segment_cnt = datalength//1000
    segment = []
    for i in range(segment_cnt):
        segment.append(data[i*1000:(i+1)*1000])
    if datalength%1000!=0:
        segment.append(data[segment_cnt*1000:])
    segment_cnt = len(segment)

    ###start sending
    while True:
        if restart is True:
            for i in range(lastack,lastack+window):
                if i>=segment_cnt+1:
                    break
                if i>=lastsent:
                    printlog('send','data','#'+str(i)+',','winSize = '+str(window))
                else:
                    printlog('resend','data','#'+str(i)+',','winSize = '+str(window))
                send_msg(sock,pack_tcp(i,0,0,segment[i-1]),target_ip,target_port)
                if i>lastsent:
                    lastsent = i
                startsend = i+1
            starttime = time.time()*10000000
            restart = False
        if  select.select([sock,],[],[],0)[0]:
            msg = recv_msg(sock)
            ack = unpack_tcp(msg[0])
            if ack[1]==0:
                print('?')
                continue
            if ack[2]==1:
                printlog('recv','finack')
                exit()
            printlog('recv','ack','#'+str(ack[0]))
            if ack[1]==lastack:
                starttime = time.time()*10000000
                lastack+=1
                if window<thres:
                    window*=2
                else:
                    window+=1
                if lastack==segment_cnt+1:
                        printlog('send','fin')
                        send_msg(sock,pack_tcp(0,0,1,b''),target_ip,target_port)
                        break
                for i in range(startsend,lastack+window):
                    if i>=segment_cnt+1:
                        break
                    printlog('send','data','#'+str(i)+',','winSize = '+str(window))
                    send_msg(sock,pack_tcp(i,0,0,segment[i-1]),target_ip,target_port)
                    lastsent = i
                    startsend = i+1
                starttime = time.time()*10000000
        curtime = time.time()*10000000
        if curtime-starttime>=timeout_fac:
            startsend = lastack
            thres = max(window//2,1)
            printlog('time','out,','','threshold = '+str(thres))
            window = 1
            restart = True


main()
