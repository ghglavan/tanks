from .gg_server import GGServer
from .gg_p import MessageType, Directions
from threading import Thread, Event, Lock
from struct import pack, unpack
from time import time, localtime
from math import sqrt
from socket import inet_aton
from random import randint


class MainService(GGServer):
    
    def __init__(self, proto_id, addr, servers, params, positions, server_updates):
        super(MainService, self).__init__(proto_id, addr)

        self.positions = positions

        self.server_updates = server_updates

        self.last_pos_update = time()

        #TODO: Combine servers with servers_addr
        self.servers = servers

        self.servers_addr = {}

        self.clients = {}

        self.clients_id = 0
        self.servers_id = 0

        self.height = params['height']
        self.width  = params['width']
        self.d_tank = params['d_tank']
        self.update_interval = params['u_interval']

        self.updates_lock = Lock()
        self.updates_wotking = Thread(target=self.__update_servers)
        self.updates_wotking_e = Event()


    def __del__(self):
        self.updates_wotking_e.set()

    def __update_servers(self):
        
        
        if self.update_interval is None:
            return

        print("[Main Service]: -STARTING UPDATE THREAD")

        while not self.updates_wotking_e.is_set():
            
            # update connections if needed
            now = time()

            if now - self.last_pos_update >= self.update_interval:
                print("[Main Service]: -updating connections")
                with self.updates_lock:
                    self.server_updates.update_connections()
                    for client in self.clients.values():
                        pos = [client["x"], client["y"]]
                        addr_id = self.server_updates.get_server(pos, client["id"])
                        addr = self.servers[addr_id]

                        if addr != client["server"]:
                            server, port = addr 
                            b_server = inet_aton(server)
                            b_port   = pack('=I', port)

                            print("[Main Service]: -Reconnectiong user with addr {} to {}".format(client["addr"], addr))

                            m_t = pack('=B', int(MessageType.ConnectTo))
                            m_t = m_t + b_server + b_port
                            q = unpack('=BBBBBI', m_t)
                            print("[Main Service]: -q e {}".format(q))
                            self.gudp_s.send_to(m_t, client["addr"])
                            client["server"] = addr
            
                self.last_pos_update = now

    def start(self):
        self.add_hook(MessageType.UserConnected, self.__on_client_connect)
        self.add_hook(MessageType.UserFired, self.__on_fire)
        self.add_hook(MessageType.UsersUpdate, self.__on_position_update)
        self.add_hook(MessageType.UserDisconnected, self.__on_disconnect)
        self.add_hook(MessageType.UserKilled, self.__on_killed)
        self.add_hook(MessageType.RequestPosition, self.__on_request_position)
        self.add_hook(MessageType.ServerConnect, self.__on_server_connect)

        self.updates_wotking.start()
        self._start()


    def __on_server_connect(self, data, addr):
        
        #TODO: check if addr is correct
        
        if addr in self.servers_addr:
            return

        print("[Main Service]: -Server {} connecting. got id {}".format(addr, self.servers_id))

        self.servers_addr[addr] = {}

        m_t = pack('=BI', int(MessageType.ServerApprove),self.servers_id)
        self.gudp_s.send_to(m_t, addr)

        self.servers_id += 1

    def __on_request_position(self, data, addr):
        u_id = unpack('=B', data)

        print("[Main Service]: -Server {} requested position of {}".format(addr, u_id))

        user = self.clients[u_id]

        x, y, o = user["x"], user["y"], user["o"]


        m_t = pack("=BIIIB", int(MessageType.RequestPosition), u_id, x, y, o)
        self.gudp_s.send_to(m_t, addr)

    def __on_client_connect(self, data, addr):


        print("[Main Service]: -user connected")

        u_id = self.clients_id

        pos = self.positions[u_id]

        with self.updates_lock:
            server_id = self.server_updates.get_server(pos, u_id)

        print("server _id : {}".format(server_id))

        server, port = self.servers[server_id]

        x, y = (pos[0], pos[1])

        o = Directions.UP

        b_server = inet_aton(server)
        b_port   = pack('=I', port)


        print("[Main Service]: -User with add {} connected. Got id {} and server {}".format(addr, u_id, server))

        m_t = pack('=BIIBI', int(MessageType.UserID), x, y, o, u_id)
        m_t = m_t + b_server + b_port
        q = unpack('=BIIBIBBBBI', m_t)
        print("[Main Service]: -q e {}".format(q))
        self.gudp_s.send_to(m_t, addr)

        self.clients_id += 1

        client = { "x" : x,
                "y" : y,
                "o" : o,
                "addr": addr,
                "id" : u_id ,
                "server": (server, port)
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
                print("[Main Service]: -reporting to {} with id {} that {} is connected and has pos {}"\
                .format(addr, u_id, client["id"], (client['x'],client['y'])))
                packed_clients += pack_client(client)

        pack_clients_l = pack("=I", len(self.clients)-1)

        m_t = clients_s + pack_clients_l + packed_clients

        self.gudp_s.send_to(m_t, addr)



    def __on_position_update(self, data, addr):
        print("[Main Service]: -got position update")
        u_id, x, y, o, l = unpack('=IIIBd', data)

        self.clients[u_id]["x"]  = x
        self.clients[u_id]["y"]  = y
        self.clients[u_id]["o"]  = o
        self.clients[u_id]["lu"] = l

        for client in self.clients.values():
            m_t = pack("=BIIBId", int(MessageType.UsersUpdate), x, y, o, u_id, l)
            print("[Main Service]: -sending position update from {} to {} - {}".format(u_id, client["id"], client["addr"]))
            self.gudp_s.send_to(m_t, client["addr"])


    def __on_fire(self, data, addr):
        u_id, x, y, o, l = unpack('=IIIBd', data)

        for client in self.clients.values():
            m_t = pack("=BIIBId", int(MessageType.UserFired), x, y, o, u_id, l)
            print("[Main Service]: -Sending fire report from {} to {} - {}".format(u_id, client["id"], client["addr"]))
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
        
        print("[Main Service]: -Client {} with addr {} diconnected.".format(c_id, self.clients[c_id]["addr"]))

        self.clients.pop(c_id, None)

        for client in self.clients.values():
            if client['addr'] != addr:
                m_t = pack("=BId", int(MessageType.UserDisconnected), c_id, time())

                self.gudp_s.send_to(m_t, client["addr"])

    