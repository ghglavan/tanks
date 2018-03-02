from .gudp_proto import Server
from .gg_p import MessageType
from threading import Thread, Event
from struct import pack, unpack
from time import time, localtime
from math import sqrt
from directions import Directions

class GGServer:

    BULLET_SPEED   = 1
    KILL_MAX_DELAY = 1 

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
        self.add_hook(MessageType.UserFired, self.__on_fire)
        self.add_hook(MessageType.UsersUpdate, self.__on_position_update)
        self.add_hook(MessageType.UserDisconnected, self.__on_disconnect)
        self.add_hook(MessageType.UserKilled, self.__on_killed)
        self.r_w_t.start()

    def join(self):
        self.r_w_t.join()

    def __on_disconnect(self, data, addr):
        c_id = self.clients[addr]["id"]
        
        print("Client {} with addr {} diconnected.".format(c_id, addr))

        self.clients.pop(addr, None)

        for cl_addr in self.clients.keys():
            if cl_addr != addr:
                m_t = pack("=BId", int(MessageType.UserDisconnected), c_id, time())

                self.gudp_s.send_to(m_t, cl_addr)
        

    def __on_killed(self, data, addr):
        k_id, l = unpack('=Id', data)

        k_addr = None

        for addr, client in self.clients.items():
            if client["id"] == k_id:
                k_addr = addr
                killed = client
                break

        killer = self.clients[addr]

        print("User with addr {} reported a kill on {} with addr {}"\
        .format(addr, k_id, k_addr))

        if k_addr == None:
            print("[Kill] No user with id {}".format(k_id))
            return

        if l > time():
            print("[Kill] Error killing(ts too big): {}, now: {}".format(l,\
            time()))
            return

        # TODO: Validate the report: 
        #distance = sqrt((killed["x"] - killer["x"])**2 + \
        #(killed["y"] - killer["y"])**2)
        
        #time = 

        for cl_addr in self.clients.keys(): 
            m_t = pack("=BId", int(MessageType.UserKilled), k_id, time())

            self.gudp_s.send_to(m_t, cl_addr)

        self.clients.pop(k_addr, None)




    def __on_fire(self, data, addr):
        x, y, o, l = unpack('=IIBd', data)

        c_lf = self.clients[addr]["lf"]
        c_id = self.clients[addr]["id"]

        print("User {} with addr {} reported that he fired"\
        .format(c_id, addr))

        if l < c_lf or l - c_lf < 2 or l > time():
            print("Error registering fire c_lf: {}, l: {}"\
            .format(c_lf, l))
            return

        bullet = {
            "x"  : x,
            "y"  : y,
            "o"  : o,
            "ts" : l,
        }

        self.clients[addr]["lf"] = c_lf
        self.clients[addr]["bullets"].append(bullet)

        for cl_addr in self.clients.keys():
            if cl_addr != addr:
                m_t = pack("=BIIBId", int(MessageType.UserFired), x, y, o, c_id, time())

                self.gudp_s.send_to(m_t, cl_addr)


    def __on_position_update(self, data, addr):
        x, y, o, l = unpack('=IIBd', data)
        old_ud = self.clients[addr]["lu"]

        print("User {} with addr {} reported a position update to {}"\
        .format(self.clients[addr]["id"], addr, (x,y,Directions(o))))

        if old_ud > l or l - old_ud < 0.05 or l > time():
            print("Error updating poz old_ud: {}, l: {}, {}, {}"\
            .format(old_ud, l, l-old_ud, l-old_ud < 0.1))
            return

        self.clients[addr]["x"]  = x
        self.clients[addr]["y"]  = y
        self.clients[addr]["o"]  = o
        self.clients[addr]["lu"] = l

        c_id = self.clients[addr]["id"]

        for cl_addr in self.clients.keys():
            if cl_addr != addr:
                m_t = pack("=BIIBId", int(MessageType.UsersUpdate), x, y, o, c_id, time())
                print("sending position update to {}".format(cl_addr))
                self.gudp_s.send_to(m_t, cl_addr)

    def __on_client_connect(self, data, addr):
        
        x, y, o, l = unpack("=IIBd", data)

        print("Client with addr {} connected. Got id {}"\
        .format(addr, self.clients_id))

        poz = { "x" : x,
                "y" : y,
                "o" : o,
                "id": self.clients_id,
                "lu": l,
                "lf": 0.0, 
                "bullets": []
                } 

        m_t = pack("=BI", int(MessageType.UserID), self.clients_id)

        self.gudp_s.send_to(m_t, addr)

        if addr not in self.clients.keys():
            self.clients[addr] = poz 

        for cl_addr in self.clients.keys():
            if cl_addr != addr:
                m_t = pack("=BIIBI", int(MessageType.UserConnected), poz["x"], poz["y"], poz["o"], poz["id"])

                self.gudp_s.send_to(m_t, cl_addr)

        def pack_client(user):
            return pack("=IIBI", user['x'], user['y'], user['o'], user['id'])

        clients_s = pack("=B", int(MessageType.UsersPositios))
        
        packed_clients = "".encode()
        for client in self.clients.values():
            if client["id"] != self.clients[addr]["id"]:
                print("reporting to {} with id {} that {} is connected and has pos {}"\
                .format(addr, self.clients[addr]["id"], client["id"], (client['x'],client['y'])))
                packed_clients = pack_client(client)

        pack_clients_l = pack("=I", len(self.clients)-1)

        m_t = clients_s + pack_clients_l + packed_clients

        self.gudp_s.send_to(m_t, addr)

        self.clients_id += 1
  

    def __recv_working(self):
        while True:
            (msg, addr) = self.gudp_s.recv()
            
            if msg is None or len(msg) < 2:
                continue
            (m_type, ), data = unpack("=B", msg[:1]), msg[1:]

            if MessageType(m_type) != MessageType.UserConnected and \
                addr not in self.clients.keys():
                continue

            if MessageType(m_type) in self.hooks:
                self.hooks[m_type](data, addr)

            if self.r_w_e.is_set():
                return