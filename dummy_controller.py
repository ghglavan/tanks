import sys

from gg_proto import GGClient, MessageType, Directions
from threading import Event, Thread, Lock
from struct import pack,unpack
from time import time

class DummyController:
    def __init__(self,
                proto_id, 
                addr, 
                s_addr,
                delay = 0.09):
        
        self.gg_c               = GGClient(proto_id, addr, s_addr)
        self.id                 = None
        self.delay              = delay

        self.connect_start      = None
        self.connect_end        = None
        self.connect_event      = Event()

        self.update_start       = None
        self.update_end         = None
        self.update_event       = Event()
        
        self.kill_start         = None
        self.kill_end           = None
        self.kill_event         = Event()
        self.kill_report_id     = None

        self.reconnect_start    = []
        self.reconnect_end      = []
        self.reconnect_lock     = Lock()
        self.reconnect_count    = 0

        self.server             = None

    def get_conn_interval(self):
        self.connect_event.wait()
        self.connect_event.clear()

        return (self.connect_start, self.connect_end)


    def get_update_interval(self):
        self.update_event.wait()
        self.update_event.clear()

        return (self.update_start, self.update_end)


    def get_kill_interval(self):
        self.kill_event.wait()
        self.kill_event.clear()

        return (self.kill_start, self.kill_end)


    def get_reconnect_intervals(self):
        with self.reconnect_lock:
            return (self.reconnect_start, self.reconnect_end)


    def start(self):
        self.gg_c.add_hook(MessageType.UserDisconnected, self.__on_user_kill_disc)
        self.gg_c.add_hook(MessageType.UserKilled, self.__on_user_kill_disc)
        self.gg_c.add_hook(MessageType.UsersUpdate, self.__on_user_update)

        self.gg_c.add_hook(MessageType.ConnectTo, self.__connect_to)

        self.connect_start = time()
        self.__connect()

    def __on_user_kill_disc(self, data):
        
        uid, t = unpack('=Id', data)

        print("got kill")

        if uid != self.kill_report_id:
            return
        
        self.kill_end = time()
        self.kill_event.set()
        self.kill_report_id = None
        

    def __connect_to(self, data):

        s1, s2, s3, s4, s_port = unpack("=BBBBI",data)
        s_addr = str(s1) + "." + str(s2) + "." + str(s3) + "." + str(s4)

        with self.reconnect_lock:
            self.reconnect_start.append(time())
            self.reconnect_count += 1

        #print("[Controller]: -reconnecting to {}".format((s_addr, s_port)))
        self.server = (s_addr, s_port)

        self.__disconnect()
        self.gg_c.connect_to_server(s_addr, s_port)

        with self.reconnect_lock:
            self.reconnect_end.append(time())


    def report_kill(self, k_id):

        self.kill_start = time()
        self.kill_report_id = k_id

        print("[Controller]: -Reporting kill on {}".format(k_id))
        m_t = pack("=BId", int(MessageType.UserKilled), k_id, time())
        self.gg_c.send(m_t)

    def report_update(self, x, y):
        print("[Controller]: -updating with {}".format( (x, y)))
        self.update_start = time()


        m_t = pack("=BIIBd", int(MessageType.UsersUpdate), x, 
                                y, Directions(0), time())
        self.gg_c.send(m_t)

    def __on_user_update(self,data):
        x, y, o, uid, t = unpack('=IIBId', data)

        if uid != self.id:
            return

        print("[Controller]: -User update")
        
        if not self.update_event.is_set():
            self.update_event.set()
            self.update_end = time()

    def __connect(self):
        print("[Controller]: -Connecting to main server")
        self.gg_c.connect()
        print("[Controller]: -Connected")
        self.x, self.y, o, self.id = self.gg_c.wait_id()
        self.server = self.gg_c.server
        self.connect_end = time()
        self.connect_event.set()

    def __disconnect(self):
        #print("[Controller]: -Reporting")
        m_t = pack("=I", int(MessageType.UserDisconnected))
        self.gg_c.send(m_t)