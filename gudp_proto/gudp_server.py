import socket
from gudp_proto.packet import Packet
from gudp_proto.gudp import Gudp


class Server(object):
    def __init__(self, proto_id, ip_addr, port):
        self.proto_id = proto_id
        self.ip_addr  = ip_addr
        self.port     = port

        self.clients  = {}


        self.socket   = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip_addr, self.port))
        self.socket.settimeout(10)


    def close(self):
        for client in self.clients.values():
            client.close()

        self.clients = {}

    def __del__(self):
        self.close()

    def recv(self):

        try:
            data, addr = self.__recv(1024)
        except:
            return (None, (None, 0))
        

        packet = Packet()
        packet.unpack(data)

        if packet.prot_id != self.proto_id:
            return self.recv()

        if addr not in self.clients.keys():
            ip_addr, port = addr
            self.clients[addr] = Gudp( 
                            self.proto_id,
                            self.ip_addr,
                            self.port,
                            ip_addr,
                            port,
                            self.socket
                        )

        self.clients[addr].recv(packet)

        return (data, addr)

    def send_to(self, data, addr):
        if addr not in self.clients.keys():
            ip_addr, port = addr
            self.clients[addr] = Gudp( 
                            self.proto_id,
                            self.ip_addr,
                            self.port,
                            ip_addr,
                            port,
                            self.socket
                        )
        
        self.clients[addr].send(data)


    def __recv(self, buf_l):
        try: 
            return self.socket.recvfrom(buf_l)
        except:
            raise


        