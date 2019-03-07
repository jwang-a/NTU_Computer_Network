import socket
import random as rand
import requests as rqst
import sys
import select
import pickle
from ctypes import *
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
    print(action.ljust(8,' ')+dtype.ljust(8,' ')+serial.ljust(8,' ')+additional)

class header(Structure):
    _fields_ = [("length",c_int),
                ("seqNumber",c_int),
                ("ackNumber",c_int),
                ("fin",c_int),
                ("syn",c_int),
                ("ack",c_int)]

class segment(Structure):
    _fields_ = [("head",header),
                ("data",c_char*1000)]

def pack_tcp(seq_num,ack_num,fin,payload):
    HDR = header(len(payload),seq_num,ack_num,fin,0,ack_num!=0)
    SGM = segment(HDR,payload)
    return SGM

def unpack_tcp(msg):
    SGM = segment.from_buffer_copy(msg)
    formated = [SGM.head.seqNumber , SGM.head.ackNumber , SGM.head.fin , SGM.data]
    return formated

