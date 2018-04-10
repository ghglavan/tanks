from .gg_server import GGServer
from .gg_p import MessageType, Directions
from threading import Thread, Event
from struct import pack, unpack
from time import time, localtime
from math import sqrt
from socket import inet_aton


class MainService(GGServer):
    
    def __init__(self, proto_id, addr, servers):
        super(MainService, self).__init__(proto_id, addr)

        #TODO: Combine servers with servers_addr
        self.servers = servers

        self.servers_addr = {}

        self.clients = {}

        self.clients_id = 0
        self.servers_id = 0


    def start(self):
        self.add_hook(MessageType.UserConnected, self.__on_client_connect)
        self.add_hook(MessageType.UserFired, self.__on_fire)
        self.add_hook(MessageType.UsersUpdate, self.__on_position_update)
        self.add_hook(MessageType.UserDisconnected, self.__on_disconnect)
        self.add_hook(MessageType.UserKilled, self.__on_killed)
        self.add_hook(MessageType.RequestPosition, self.__on_request_position)
        self.add_hook(MessageType.ServerConnect, self.__on_server_connect)
        self._start()


    def __on_server_connect(self, data, addr):
        
        #TODO: check if addr is correct
        
        if addr in self.servers_addr:
            return

        print("Server {} connecting. got id {}".format(addr, self.servers_id))

        self.servers_addr[addr] = {}

        m_t = pack('=BI', int(MessageType.ServerApprove),self.servers_id)
        self.gudp_s.send_to(m_t, addr)

        self.servers_id += 1

    def __on_request_position(self, data, addr):
        u_id = unpack('=B', data)

        print("Server {} requested position of {}".format(addr, u_id))

        user = self.clients[u_id]

        x, y, o = user["x"], user["y"], user["o"]


        m_t = pack("=BIIIB", int(MessageType.RequestPosition), u_id, x, y, o)
        self.gudp_s.send_to(m_t, addr)

    def __on_client_connect(self, data, addr):


        print("user connected")

        #TODO: decide x,y,o
        #TODO: decide the server 
        u_id = self.clients_id

        if u_id % 2 == 0:
            x = 0
            y = 0
            o = Directions.UP
            server, port = self.servers[0]
        else:
            x = 100
            y = 100
            o = Directions.UP
            server, port = self.servers[1]


        b_server = inet_aton(server)
        b_port   = pack('=I', port)



        print("User with add {} connected. Got id {} and server {}".format(addr, u_id, server))

        m_t = pack('=BIIBI', int(MessageType.UserID), x, y, o, u_id)
        m_t = m_t + b_server + b_port
        q = unpack('=BIIBIBBBBI', m_t)
        print("q e {}".format(q))
        self.gudp_s.send_to(m_t, addr)

        self.clients_id += 1

        client = { "x" : x,
                "y" : y,
                "o" : o,
                "addr": addr,
                "id" : u_id ,
                "server": server
                }

        self.clients[u_id] = client

        for client in self.clients.values():
            if client["addr"] != addr:
                m_t = pack("=BIIBI", int(MessageType.UserConnected), x, y, o, u_id)

                self.gudp_s.send_to(m_t, client["addr"])

        def pack_client(user):
            return pack("=IIBI", user['x'], user['y'], user['o'], user['id'])

        clients_s = pack("=B", int(MessageType.UsersPositions))
        
        packed_clients = "".encode()
        for client in self.clients.values():
            if client["id"] != u_id:
                print("reporting to {} with id {} that {} is connected and has pos {}"\
                .format(addr, u_id, client["id"], (client['x'],client['y'])))
                packed_clients += pack_client(client)

        pack_clients_l = pack("=I", len(self.clients)-1)

        m_t = clients_s + pack_clients_l + packed_clients

        self.gudp_s.send_to(m_t, addr)



    def __on_position_update(self, data, addr):
        print("got position update")
        u_id, x, y, o, l = unpack('=IIIBd', data)

        self.clients[u_id]["x"]  = x
        self.clients[u_id]["y"]  = y
        self.clients[u_id]["o"]  = o
        self.clients[u_id]["lu"] = l

        for client in self.clients.values():
            m_t = pack("=BIIBId", int(MessageType.UsersUpdate), x, y, o, u_id, l)
            print("sending position update from {} to {} - {}".format(u_id, client["id"], client["addr"]))
            self.gudp_s.send_to(m_t, client["addr"])


    def __on_fire(self, data, addr):
        u_id, x, y, o, l = unpack('=IIIBd', data)

        for client in self.clients.values():
            m_t = pack("=BIIBId", int(MessageType.UserFired), x, y, o, u_id, l)
            print("Sending fire report from {} to {} - {}".format(u_id, client["id"], client["addr"]))
            self.gudp_s.send_to(m_t, client["addr"])


    def __on_killed(self, data, addr):
        u_id, k_id, l = unpack('=IId', data)

        k_addr = self.clients[k_id]["addr"]

        if k_addr != addr:
            m_t = pack("=BId", int(MessageType.ServerKillUser), k_id, l)
            self.gudp_s.send_to(m_t, k_addr)


        for client in self.clients.values(): 
            m_t = pack("=BId", int(MessageType.UserKilled), k_id, l)

            self.gudp_s.send_to(m_t, client["addr"])

        self.clients.pop(k_addr, None)


    def __on_disconnect(self, data, addr):
        c_id = unpack('=I', data)
        
        print("Client {} with addr {} diconnected.".format(c_id, self.clients[c_id]["addr"]))

        self.clients.pop(c_id, None)

        for client in self.clients.values():
            if cl_addr != addr:
                m_t = pack("=BId", int(MessageType.UserDisconnected), c_id, time())

                self.gudp_s.send_to(m_t, client["addr"])

    