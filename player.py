from gg_proto import GGClient

class Player:
    def __init__(self,tank):
        self.tank = tank.copy()

    def bind_and_connect(self, proto_id, addr, s_addr):
        self.gg_client = GGClient(proto_id, addr, s_addr)
        self.gg_client.connect()

    