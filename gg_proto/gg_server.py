from .gudp_proto import Server
from .gg_p import MessageType
from threading import Thread, Event
from struct import *

class GGServer:
    def __init__(self, proto_id, addr):
        
        self.ip_addr, self.port = addr
        self.gudp_s = Server(proto_id, 
                            self.ip_addr, 
                            self.port)

        self.clients_id = 0

        self.clients    = {}

        self.hooks      = {}

        self.r_w_t  = Thread(target=self.__recv_working)
        self.r_w_e  = Event()
    
    def add_hook(self,m: MessageType, f):
        self.hooks[m] = f

    def start(self):
        self.add_hook(MessageType.UserConnected, self.__on_client_connect)
        self.r_w_t.start()

    def join(self):
        self.r_w_t.join()

    def __on_client_connect(self, data, addr):

        print("len: {}".format(len(data)))
        
        x, y, o = unpack("=IIB", data)

        print("vhfhjjgf")

        poz = { "x" : x,
                "y" : y,
                "o" : o,
                "id": self.clients_id} 

        m_t = pack("=BI", int(MessageType.UserID), self.clients_id)

        self.gudp_s.send_to(m_t, addr)

        if addr not in self.clients.keys():
            self.clients[addr] = poz 

        for cl_addr in self.clients.keys():
            if cl_addr != addr:
                m_t = pack("=BIIBI", int(MessageType.UserConnected), poz["x"], poz["y"], poz["o"], poz["id"])

                self.gudp_s.send_to(m_t, cl_addr)


        self.clients_id += 1
  

    def __recv_working(self):
        while True:
            (msg, addr) = self.gudp_s.recv()
            
            if msg is None or len(msg) < 2:
                continue

            print("msg len: {}".format(len(msg)))
            (m_type, ), data = unpack("=B", msg[:1]), msg[1:]


            print("Got a message: {}, mtype: {}, data: {}".format(msg, MessageType(m_type), data))

            if MessageType(m_type) in self.hooks:
                print("calling")
                self.hooks[m_type](data, addr)

            if self.r_w_e.is_set():
                return