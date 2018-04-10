from .gudp_proto import Server
from .gg_p import NoHooksRegistered, MessageType
from threading import Thread, Event
from struct import pack, unpack
from time import time, localtime

class GGServer:

    def __init__(self, proto_id, addr):
        
        self.ip_addr, self.port = addr
        self.gudp_s = Server(proto_id, 
                            self.ip_addr, 
                            self.port)

        self.clients    = {}

        self.servers_addr = {}

        self.hooks      = {}

        self.r_w_t  = Thread(target=self.__recv_working)
        self.r_w_e  = Event()
    
    def __del__(self):
        self.r_w_e.set()

    def add_hook(self,m: MessageType, f):
        self.hooks[m] = f

    def _start(self):
        if self.hooks == {}:
            raise NoHooksRegistered

        print("starting rwt")
        self.r_w_t.start()

    def join(self):
        self.r_w_t.join()


    def __recv_working(self):
        while not self.r_w_e.is_set():
            (msg, addr) = self.gudp_s.recv()
            if msg is None or len(msg) < 1:
                continue
            (m_type, ), data = unpack("=B", msg[:1]), msg[1:]

            if MessageType(m_type) != MessageType.UserConnected and \
                MessageType(m_type) != MessageType.ServerConnect and \
                addr not in self.clients.keys() and addr not in self.servers_addr.keys():
                continue

            if MessageType(m_type) in self.hooks:
                self.hooks[m_type](data, addr)
