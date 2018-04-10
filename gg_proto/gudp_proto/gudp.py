"""

    Gudp

    Gudp is a class that implements a virtual connection over udp

    a gudp packet is an udp packet with an extra header:
        proto_id -- 4 bytes
        seq      -- 4 bytes
        ack      -- 4 bytes
        ack_bits -- 4 bytes

    This virtual connection ensures reliability.

    For more details: https://gafferongames.com/post/reliability_ordering_and_congestion_avoidance_over_udp/

"""

# TODO: implement congestion avoidance (make a queue for recv and use its length to request a lower 
#  pps from remote)


import socket
import threading
import struct
import sys

from queue import Queue
from time  import time

from .packet import Packet,seq_gt,add_to_seq,sub_from_seq

class Fixed_Q(object):
    def __init__(self, len):
        self.len  = len
        self.size = 0
        self.q    = []

    def push(self, x):
        if self.size == self.len:
            self.q.pop()
            self.size -= 1
        
        self.q.insert(0, x)
        self.size += 1

    def in_q(self, x):
        return x in self.q


class Gudp(object):

    #TODO: make ip_addr,port and s_ip_addr, s_port tuples 

    MAX_Q_SIZE = 120
    RESEND_INTERVAL = 1

    def __init__(self, 
            proto_id  = 1, 
            ip_addr   = "", 
            port      = 0,
            s_ip_addr = "", 
            s_port    = 0,
            s_sock    = None):

        self.ip_addr    = ip_addr
        self.port       = port       
        self.s_ip_addr  = s_ip_addr
        self.s_port     = s_port
        
        self.remote_seq = 0

        self.proto_id   = proto_id

        self.recv_seq   = Fixed_Q(32)

        self.seq      = 100

        self.send_pack  = {}
        self.send_p_lock= threading.Lock() 

        if s_sock is None:
            self.s   = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )

            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.ip_addr != "" and self.port != 0:
                 self.s.bind((self.ip_addr, self.port))
            #TODO make timeout an argument
            self.s.settimeout(10)
        else:
            self.s = s_sock

        self.gudp_sendq = Queue(Gudp.MAX_Q_SIZE)  

        self.s_w_ctl  = threading.Thread(target=self.__send_worker)
        self.s_w_s_ev = threading.Event()
        self.s_w_ctl.start()

        # self.t = threading.Timer(1, self.__resend)
        # self.t.start()

    def __del__(self):
        self.close()

    def close(self):
        #self.t.cancel()
        self.s_w_s_ev.set()
        self.s_w_ctl.join()

    def recv(self, p: Packet = None):

        
        if p is None:
            try:
                data, addr = self.s.recvfrom(1024)
            except:
                return (None, (None, 0))
            
            if addr != (self.s_ip_addr, self.s_port):
                return self.recv()


            packet = Packet()
            try:
                packet.unpack(data)
            except:
                return self.recv()

            if packet.prot_id != self.proto_id:
                return self.recv()
        else:
            packet = p
            

        if seq_gt(packet.seq, self.remote_seq):
            self.remote_seq = packet.seq
        
        self.recv_seq.push(packet.seq)

        with self.send_p_lock:
            if packet.ack in self.send_pack.keys():
                    self.send_pack.pop(packet.ack, None)     


            for i in range(0, 32):
                if 1<<i & packet.ack_bit == 1:
                    if sub_from_seq(packet.ack, i+1) in self.send_pack.keys():
                            self.send_pack.pop(sub_from_seq(packet.ack, i+1), None)

        if p is None:
            return (packet.data, addr)
        else:
            return (packet.data, ("", 0))

    def send(self, data):
        packet = Packet()

        packet.ack = self.remote_seq
            
        packet.seq = self.seq
        self.seq = add_to_seq(self.seq, 1)

        seq_mask = 0

        for s in range(self.remote_seq - self.recv_seq.len, self.remote_seq):
            if self.recv_seq.in_q(s):
                subed = sub_from_seq(self.remote_seq, s)
                seq_mask = seq_mask | 1<<(subed -1)
            
            
        packet.ack_bit = seq_mask

        packet.prot_id = self.proto_id
        packet.data    = data

        with self.send_p_lock:
            self.send_pack[packet.seq] = packet

        try:
            self.gudp_sendq.put_nowait(packet)
        except:
            print("[GUDP] QUEUE FULL!! Maybe try a larger size")
            exit(1)


    def __resend(self):

        sent = False

        with self.send_p_lock:
            for p in self.send_pack.values():
                try:
                    self.gudp_sendq.put_nowait(p)
                    sent = True
                except:
                    print("[GUDP] QUEUE FULL!! Maybe try a larger size ")
                    exit(1)
            
            self.send_pack = {}
        
        return sent

                

    def __send_worker(self):
        last_resend = time()

        while not self.s_w_s_ev.is_set():
            now = time()

            if now - last_resend >= Gudp.RESEND_INTERVAL:
                #if not self.__resend():
                #    self.send(b"")
                self.__resend()    
                last_resend = now
            

            try:
                packet = self.gudp_sendq.get_nowait()
            except:
                continue

            if packet is not None:
                self.__send(packet.pack())

            #TODO: if there are still packets in proto_q.. do we
            # want to send them when the gudp object is destructed?


    def __send(self, message):
        self.s.sendto(message, 
        (self.s_ip_addr, self.s_port))

