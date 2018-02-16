from gudp_proto.gudp import Gudp

class Client:
    def __init__(self, proto_id, ip_addr, port,
                     s_ip_addr, s_port):
        
        self.gudp_c = Gudp(
            proto_id,
            ip_addr,
            port,
            s_ip_addr,
            s_port
        )

    def __del__(self):
        self.gudp_c.close()

    def send(self, data):
        self.gudp_c.send(data)
    
    def recv(self):
        return self.gudp_c.recv()
