"""
    Gudp_q

    GudpQ is a class that implements a packet queue

    GudpQ.add_to_q adds a new packet at the end of the queue
    GudpQ.get_from_q pops the last packet from this queue

"""


import socket

from threading import Lock
from gudp_proto.packet import Packet


class GudpQ(object):
    def __init__(self, proto_id = 1) :
        self.proto_id      = proto_id
        self.message_queue = []
        self.message_lock  = Lock()


    def add_to_q(self, msg: Packet):
        with self.message_lock:
            self.message_queue.append(msg)

    def get_from_q(self):
        with self.message_lock:
            try:
                return self.message_queue.pop()
            except:
                return None