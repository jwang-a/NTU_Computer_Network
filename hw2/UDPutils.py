import socket
import random as rand
import requests as rqst
import sys
import select
import pickle
from pwn import *

def init_srv(ip,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip,port))
    return sock

def recv_msg(sock):
    return sock.recvfrom(2048)

def send_msg(sock,msg,target_ip,target_port):
    sock.sendto(msg,(target_ip,target_port))

def printlog(action,dtype='',serial='',additional=''):
    print(action.ljust(8,' ')+dtype.ljust(8,' ')+serial.ljust(10,' ')+additional)

def pack_tcp(seq_num,ack_num,fin,payload):
    check = [payload[i] for i in range(len(payload))]
    checksum = ((sum(check[0::2])+(sum(check[1::2])<<8))&65536)^65536
    segment = pickle.dumps([seq_num,ack_num,fin,checksum,payload])
    return segment

def unpack_tcp(msg):
    segment = pickle.loads(msg)
    check = [segment[4][i] for i in range(len(segment[4]))]
    check = ((sum(check[0::2])+(sum(check[1::2])<<8))&65536)
    if check|segment[3] != 65536:
        segment[1] = 'bad'
    return segment
    
