from .gg_server import GGServer
from .gg_p import MessageType, Directions
from .gudp_proto import Client 
from threading import Thread, Event
from struct import pack, unpack
from time import time, localtime
from math import sqrt

from .servers_update_controllers import KNNServersUpdate, RandomServersUpdate, KMeansServersUpdate

class GameService(GGServer):

    BULLET_SPEED   = 1
    KILL_MAX_DELAY = 1 

    def __init__(self, proto_id, b_addr, main_addr):
        
        super(GameService, self).__init__(proto_id, b_addr)

        self.m_ip_addr, self.m_port = main_addr

        self.main_service_c = Client(proto_id,
                                "",
                                0,
                                self.m_ip_addr,
                                self.m_port)

        self.main_service_hooks = {}

        self.main_service_thread = Thread(target=self.__main_server_recv)
        self.m_s_t_e = Event()

        self.id = None
        self.is_id_set = Event()

    def __del__(self):
        self.m_s_t_e.set()

    def add_main_service_hook(self, mtype, f):
        self.main_service_hooks[mtype] = f

    def start(self):
        self.add_hook(MessageType.UserConnected, self.__on_client_connect)
        self.add_hook(MessageType.UserFired, self.__on_fire)
        self.add_hook(MessageType.UsersUpdate, self.__on_position_update)
        self.add_hook(MessageType.UserDisconnected, self.__on_disconnect)
        self.add_hook(MessageType.UserKilled, self.__on_killed)
        self._start()

        self.main_service_thread.start()


        def __on_server_approve(data, addr):
            self.id, = unpack('=I', data)
            print("[Game Service]: -Connected to main_service. Got id {}".format(self.id))
            self.is_id_set.set()

        self.add_main_service_hook(MessageType.ServerApprove, __on_server_approve)

        print("[Game Service]: -Connecting to main_service...")
        m_t = pack('=B',int(MessageType.ServerConnect))
        self.main_service_c.send(m_t)
        self.is_id_set.wait()

    def __on_request_position(self, data, addr):
        u_id, x, y, o = unpack('=IIIB', data)

        if self.user_position_hooks[u_id] is not None:
            self.user_position_hooks[u_id](x, y, o, addr)

    def __on_disconnect(self, data, addr):
        c_id = self.clients[addr]["id"]
        
        print("[Game Service]: -Client {} with addr {} diconnected.".format(c_id, addr))

        self.clients.pop(addr, None)
        

    def __on_killed(self, data, addr):
        k_id, l = unpack('=Id', data)

        k_addr = None

        for addr, client in self.clients.items():
            if client["id"] == k_id:
                k_addr = addr
                killed = client
                break


        def do_check_kill(x, y, o):
            #TODO: check if kill is valid
            if l > time():
                print("[Game Service]: -[Kill] Error killing(ts too big): {}, now: {}".format(l,\
                time()))
                return False
            return True


        killer = self.clients[addr]

        print("[Game Service]: -Got kill request")

        if k_addr is None:
            m_t = pack("=BB", int(MessageType.RequestPosition), k_id)

            def __on_requested_positions(data, addr):
                uid, x, y, o = unpack('=IIIB', data)
                if do_check_kill(x, y, o):
                    print("[Game Service]: -User with addr {} reported a kill on {} with addr {} from another server"\
                    .format(addr, k_id, k_addr)) 
                    m_t = pack('=BIId', int(MessageType.UserKilled), killer["id"], k_id, l)
        
                    self.main_service_c.send(m_t) 
                

            self.add_main_service_hook(MessageType.RequestPosition, __on_requested_positions)

        else:
            print("[Game Service]: -User with addr {} reported a kill on {} with addr {}"\
            .format(addr, k_id, k_addr)) 

            self.clients.pop(k_addr, None)

            m_t = pack('=BI', int(MessageType.UserKilled), killer["id"]) + data
            
        self.main_service_c.send(m_t)        



    def __on_fire(self, data, addr):
        x, y, o, l = unpack('=IIBd', data)

        c_lf = self.clients[addr]["lf"]
        c_id = self.clients[addr]["id"]

        print("[Game Service]: -User {} with addr {} reported that he fired"\
        .format(c_id, addr))

        if l < c_lf or l - c_lf < 2 or l > time():
            print("[Game Service]: -Error registering fire c_lf: {}, l: {}"\
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

        m_t = pack('=BI', int(MessageType.UserFired), c_id) + data
        self.main_service_c.send(m_t)


    def __on_position_update(self, data, addr):
        x, y, o, l = unpack('=IIBd', data)
        old_ud = self.clients[addr]["lu"]

        print("[Game Service]: -User {} with addr {} reported a position update to {}"\
        .format(self.clients[addr]["id"], addr, (x,y,Directions(o))))

        if old_ud > l or l - old_ud < 0.01 or l > time():
            print("[Game Service]: -Error updating poz old_ud: {}, l: {}, {}, {}"\
            .format(old_ud, l, l-old_ud, l-old_ud < 0.1))
            return

        #TODO: validate position update
        
        self.clients[addr]["x"]  = x
        self.clients[addr]["y"]  = y
        self.clients[addr]["o"]  = o
        self.clients[addr]["lu"] = l

        m_t = pack('=BI', int(MessageType.UsersUpdate), self.clients[addr]["id"]) + data
        self.main_service_c.send(m_t)
        

    def __on_client_connect(self, data, addr):
        
        x, y, o, u_id, l = unpack("=IIBId", data)

        print("[Game Service]: -Client with addr {} connected. Got id {}"\
        .format(addr, u_id))

        poz = { "x" : x,
                "y" : y,
                "o" : o,
                "id": u_id,
                "lu": l,
                "lf": 0.0, 
                "bullets": []
                } 

        if addr not in self.clients.keys():
            self.clients[addr] = poz 


    def __main_server_recv(self):
        while not self.m_s_t_e.is_set():
            (msg, addr) = self.main_service_c.recv()
            print("[Game Service]: -Got {} from {}".format(msg, addr))

            if msg is None or len(msg) < 1:
                continue
            (m_type, ), data = unpack("=B", msg[:1]), msg[1:]


            if MessageType(m_type):
                self.main_service_hooks[m_type](data, addr)
                