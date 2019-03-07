import socket
import random as rand
import sys
import select
from pwn import *
from UDPutils import *



###utils
def random_drop_relay(sock,segment,msg,sender_ip,sender_port,reciever_ip,reciever_port,TTol,Drop,Drop_rate):
    if msg[1][0]==sender_ip and msg[1][1]==sender_port:
        if segment[2]==1:
            printlog('get','fin')
            printlog('fwd','fin')
            send_msg(sock,msg[0],reciever_ip,reciever_port)
            return TTol,Drop
        printlog('get','data','#'+str(segment[0]))
        TTol+=1
        if rand.random()<Drop_rate:
            Drop+=1
            printlog('drop','data','#'+str(segment[0])+',','loss rate = '+str(round(Drop/TTol,4)).ljust(6,'0'))
            return TTol,Drop
        printlog('fwd','data','#'+str(segment[0])+',','loss rate = '+str(round(Drop/TTol,4)).ljust(6,'0'))
        send_msg(sock,msg[0],reciever_ip,reciever_port)
        return TTol,Drop
    elif msg[1][0]==reciever_ip and msg[1][1]==reciever_port:
        if segment[2]==1:
            printlog('get','finack')
            printlog('fwd','finack')
            send_msg(sock,msg[0],sender_ip,sender_port)
            exit()
        printlog('get','ack','#'+str(segment[1]))
        send_msg(sock,msg[0],sender_ip,sender_port)
        printlog('fwd','ack','#'+str(segment[1]))
        return TTol,Drop
    else:
        return TTol,Drop


def main():
    ###meta ip/port
    my_ip = '127.0.0.1'
    my_port = 10102
    sender_ip = '127.0.0.1'
    sender_port = 10101
    reciever_ip = '127.0.0.1'
    reciever_port = 10103

    ###init_data
    TTol = 0
    Drop = 0
    if len(sys.argv)<2:
        print('please provide drop rate')
        exit()
    Drop_rate = float(sys.argv[1])

    ###initiate socket
    sock = init_srv(my_ip,my_port)

    ###start listening
    while True:
        msg = recv_msg(sock)
        segment = unpack_tcp(msg[0])
        TTol, Drop = random_drop_relay(sock,segment,msg,sender_ip,sender_port,reciever_ip,reciever_port,TTol,Drop,Drop_rate)


main()
