import socket
import random as rand
import sys
import select
from pwn import *
from UDPutils import *


###Utils

def main():
    ###meta ip/port
    my_ip = '127.0.0.1'
    my_port = 10103
    target_ip = '127.0.0.1'
    target_port = 10102

    ###initiate_data
    recv_buf = b''
    got_cnt = 0
    start_ind = 0

    ###initiate socket
    sock = init_srv(my_ip,my_port)

    ###prepare file
    f = open('result.jpg','wb')

    ###start listening
    while True:
        if select.select([sock,],[],[],0)[0]:
            msg = recv_msg(sock)
            segment = unpack_tcp(msg[0])
            if segment[2]==1:
                printlog('recv','fin')
                printlog('send','finack')
                send_msg(sock,pack_tcp(None,1,1,b''),target_ip,target_port)
                printlog('flush')
                f.write(recv_buf)
                break
            if segment[1]=='bad':
                printlog('adrop','data','#'+str(segment[0]))
                printlog('send','ack','#'+str(got_cnt+start_ind-1))
                send_msg(sock,pack_tcp(got_cnt+start_ind-1,1,None,b''),target_ip,target_port)
            else:
                index = segment[0]-start_ind
                if index!=got_cnt:
                    printlog('drop','data','#'+str(segment[0]))
                    printlog('send','ack','#'+str(got_cnt+start_ind-1))
                    send_msg(sock,pack_tcp(got_cnt+start_ind-1,1,None,b''),target_ip,target_port)
                    continue
                printlog('recv','data','#'+str(segment[0]))
                printlog('send','ack','#'+str(segment[0]))
                send_msg(sock,pack_tcp(segment[0],1,None,b''),target_ip,target_port)
                recv_buf+=segment[4]
                got_cnt+=1
                if got_cnt==32:
                    start_ind+=32
                    got_cnt = 0
                    printlog('flush')
                    f.write(recv_buf)
                    recv_buf = b''
                


main()
