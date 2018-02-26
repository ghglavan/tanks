from .gudp_proto import Client
from .gg_p import MessageType
from threading import Thread, Event
from struct import *

class GGClient:
    def __init__(self, 
                proto_id, 
                addr,
                s_addr):
        
        self.ip_addr, self.port     = addr
        self.s_ip_addr, self.s_port = s_addr


        self.gudp_c = Client(proto_id,
                            self.ip_addr,
                            self.port,
                            self.s_ip_addr,
                            self.s_port)

        self.hooks  = {}

        self.id     = None
        self.id_set = Event()

        self.r_w_t  = Thread(target=self.__recv_working)
        self.r_w_e  = Event()


    def __del__(self):
        self.r_w_e.set()

    def add_hook(self,m: MessageType, f):
        self.hooks[m] = f

    def connect(self):
        m_t = pack("=BIIB",int(MessageType.UserConnected), 0, 0, 0)
        print("len: {}, m_t: {}".format(len(m_t),m_t))

        self.gudp_c.send(m_t)
        self.add_hook(MessageType.UserID, self.__on_user_id)
        self.__start_recv()


    def __on_user_id(self, u_id):
        print("if len: {}".format(len(u_id)))
        (self.id, ) = unpack("I",u_id)
        self.id_set.set()


    def is_id_set(self):
        return self.id_set.is_set()

    def __start_recv(self):
        self.r_w_t.start()

    def __recv_working(self):
        while True:
            (msg, addr) = self.gudp_c.recv()
            
            if msg is None or len(msg) < 2:
                continue

            if addr != (self.s_ip_addr, self.s_port):
                continue
            
            (m_type, ), data = unpack("B",msg[:1]), msg[1:]

            print("Got a message: {}, mtype: {}, data: {}".format(msg, m_type,data))

            if MessageType(m_type) in self.hooks:
                self.hooks[m_type](data)

            if self.r_w_e.is_set():
                return