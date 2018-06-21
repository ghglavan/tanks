from .gudp_proto import Client
from .gg_p import MessageType
from threading import Thread, Event
from struct import pack, unpack
from time import time
from socket import inet_ntoa

class GGClient:
    def __init__(self, 
                proto_id, 
                addr,
                main_addr):
        
        self.ip_addr, self.port     = addr
        self.m_ip_addr, self.m_port = main_addr


        self.gudp_c = None

        self.proto_id = proto_id


        self.main_service_c = Client(proto_id,
                                self.ip_addr,
                                self.port,
                                self.m_ip_addr,
                                self.m_port)

        self.hooks  = {}

        self.id     = None
        self.x      = None
        self.y      = None
        self.o      = None


        self.id_set = Event()

        self.r_w_t  = Thread(target=self.__recv_working)
        self.r_w_e  = Event()


    def __del__(self):
        self.r_w_e.set()

    def send(self, data):
        self.gudp_c.send(data)

    def add_hook(self,m: MessageType, f):
        self.hooks[m] = f

    def connect(self):
        m_t = pack("=B",int(MessageType.UserConnected))

        self.add_hook(MessageType.UserID, self.__on_user_id)
        self.__start_recv()

        self.main_service_c.send(m_t)


    def reconnect_to_server(self, s_addr, s_port):
        self.s_addr = s_addr
        self.s_port = s_port

        self.gudp_c.change_addr(s_addr, s_port)

        #print("reconnecting gudp_c to {}-{}".format(self.s_addr, self.s_port) )
        m_t = pack("=BIIBId", int(MessageType.UserRedirected), self.x, self.y, self.o, self.id, time())
        self.gudp_c.send(m_t)

    def connect_to_server(self, s_addr, s_port):
        self.s_addr = s_addr
        self.s_port = s_port

        self.gudp_c = Client(self.proto_id,
                            self.ip_addr,
                            self.port,
                            self.s_addr,
                            self.s_port)
        
        #print("connecting gudp_c to {}-{}".format(self.s_addr, self.s_port) )
        m_t = pack("=BIIBId", int(MessageType.UserConnected), self.x, self.y, self.o, self.id, time())
        self.gudp_c.send(m_t)

    def __on_user_id(self, data):

        (self.x, self.y, self.o, self.id, s1, s2, s3, s4, s_port) = unpack("=IIBIBBBBI",data)
        s_addr = str(s1) + "." + str(s2) + "." + str(s3) + "." + str(s4)
        
        self.server = (s_addr, s_port)

        self.connect_to_server(s_addr, s_port)

        self.id_set.set()


    def is_id_set(self):
        return self.id_set.is_set()


    def wait_id(self):
        self.id_set.wait()
        return self.x, self.y, self.o, self.id

    def __start_recv(self):
        self.r_w_t.start()

    def __recv_working(self):
        while not self.r_w_e.is_set():
            (msg, addr) = self.main_service_c.recv()
            #print("Got message {} from {}".format(msg, addr))
            if msg is None or len(msg) < 2:
                continue

            if addr != (self.m_ip_addr, self.m_port):
                continue
            
            (m_type, ), data = unpack("B",msg[:1]), msg[1:]

            if MessageType(m_type) in self.hooks:
                self.hooks[m_type](data)
