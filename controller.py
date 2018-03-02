from gg_proto import GGClient, MessageType
from threading import Lock, Timer, Event
from tank import Tank
from struct import pack,unpack
from directions import Directions
from time import time
import pygame

class Controller:
    def __init__(self, 
                screen,
                p_tank_i,
                e_tank_i, 
                proto_id, 
                addr, 
                s_addr,
                bulled_dims = (3,3)):
        
        self.gg_c               = GGClient(proto_id, addr, s_addr)
        self.tanks              = {}
        self.tanks_lock         = Lock()
        self.screen             = screen
        self.died               = Event()
        self.p_tank_img         = p_tank_i
        self.e_tank_img         = e_tank_i
        self.bullet_dimentions  = bulled_dims
        self.id                 = None

        self.timed_draw_r     = Timer(0.08, self.__worker_draw_and_report)

    def __del__(self):
        self.timed_draw_r.cancel()
        self.__disconnect()

    def start(self):
        self.gg_c.add_hook(MessageType.UserConnected, self.__on_new_user)
        self.gg_c.add_hook(MessageType.UserFired, self.__on_user_fire)
        self.gg_c.add_hook(MessageType.UsersUpdate, self.__on_user_update)
        self.gg_c.add_hook(MessageType.UserDisconnected, self.__on_user_kill_disc)
        self.gg_c.add_hook(MessageType.UserKilled, self.__on_user_kill_disc)
        self.gg_c.add_hook(MessageType.UsersPositios, self.__on_users_positions)

        self.__connect()
        self.timed_draw_r.start()


    def report_update(self, x, y):
        if self.died.is_set():
            return

        tank = self.tanks[self.id]
        t_x, t_y, t_o = tank.s_move([x, y])
        print("tank is at {}, updating with {}".format(tank.rect.topleft, (t_x, t_y)))


        m_t = pack("=BIIBd", int(MessageType.UsersUpdate), t_x, 
                                t_y, t_o, time())
        self.gg_c.send(m_t)

    def report_fire(self):
        if self.died.is_set():
            return

        tank = self.tanks[self.id]
        t_x, t_y, t_o = tank.get_local_pos()

        m_t = pack("=BIIBd", int(MessageType.UserFired), t_x, 
                                t_y, t_o, time())
        
        self.gg_c.send(m_t)

    def __report_kill(self, k_id):
        print("Reporting kill on {}".format(k_id))
        m_t = pack("=BId", int(MessageType.UserKilled), k_id, time())
        self.gg_c.send(m_t)

    def __disconnect(self):
        m_t = pack("=I", int(MessageType.UserDisconnected))
        self.gg_c.send(m_t)

    def __connect(self):
        self.gg_c.connect()
        self.id = self.gg_c.wait_id()
        self.tanks[self.id] = Tank(self.id,
                                self.p_tank_img,
                                self.screen,
                                self.bullet_dimentions,
                                )

    def __on_new_user(self, data):
        x, y, o, uid = unpack('=IIBI', data)

        with self.tanks_lock:
            self.tanks[uid] = Tank(uid,
                                   self.e_tank_img,
                                   self.screen,
                                   self.bullet_dimentions,
                                   [x,y],
                                   Directions(o))

    
    def __on_user_update(self,data):
        x, y, o, uid, t = unpack('=IIBId', data)

    
        if uid not in self.tanks.keys():
            return

        tank = self.tanks[uid]
        if tank.last_update and tank.last_update > t:
            return

        old_x, old_y, _ = tank.get_pos()
        o = Directions(o)

        with self.tanks_lock:
            tank.move([x-old_x, y-old_y], t)


    def __on_user_fire(self,data):
        x, y, o, uid, t = unpack('=IIBId', data)
        
        tank = self.tanks[uid]

        if tank.last_fired and (tank.last_fired > t or t - tank.last_fired < 0.2):
            return
        
        tank.update_o(Directions(o))
        
        with self.tanks_lock:
            tank.fire(t)

    def __on_users_positions(self, data):
        print("Got users positions with {}".format(len(data)))
        
        (n_clients, ) = unpack("=I", data[:4])
        data = data[4:]

        with self.tanks_lock:
            for _ in range(0, n_clients):

                x, y, o, uid = unpack("=IIBI", data[:13])
                print("Got one user of {}. x: {}, y:{}".format(n_clients, x,y))
                self.tanks[uid] = Tank(uid,
                                    self.e_tank_img,
                                    self.screen,
                                    self.bullet_dimentions,
                                    [x,y],
                                    Directions(o))
                
                data = data[13:]

    def __on_user_kill_disc(self, data):
        uid, t = unpack('=Id', data)

        if uid == self.gg_c.id:
            self.died.set()

        with self.tanks_lock:
            self.tanks.pop(uid, None)

    def __worker_draw_and_report(self):
        
        self.screen.fill((112, 112, 112))

        with self.tanks_lock:
            if self.id is None or self.id not in self.tanks.keys():
                self.__restart_draw_timer()
                return

            our_t = self.tanks[self.id]
            their_ts  = [tank.rect for tank in self.tanks.values() if tank.id != self.id]
            their_ids = [uid for uid in self.tanks.keys() if uid != self.id]
            our_b    = [bullet.get_rect() for bullet in our_t.bullets]

            if not self.died.is_set():
                tanks_i = our_t.rect.collidelist(their_ts)
                if tanks_i != -1:
                    print("Reporting kill on {} from collision. My poz: ({}), their: ({})"\
                    .format(their_ids[tanks_i], our_t.rect.topleft, \
                    self.tanks[their_ids[tanks_i]].rect.topleft))
                    self.__report_kill(their_ids[tanks_i])
                    self.__report_kill(self.gg_c.id)
                    self.tanks.pop(their_ids[tanks_i], None)

                    del their_ids[tanks_i]
                    del their_ts[tanks_i]
                    
                    self.died.set()
                    #TODO: Say that we died and stop sending update reports

            bullet_inds = []
            for ind, bullet in enumerate(our_b):
                bullet_i = bullet.collidelist(their_ts)

                if bullet_i != -1:
                    print("Reporting kill from bullets on {}. Got him with bullet {} of {}".format(their_ids[bullet_i], ind, len(our_b)))
                    self.__report_kill(their_ids[bullet_i])
                    self.tanks.pop(their_ids[bullet_i], None)

                    del their_ids[bullet_i]
                    del their_ts[bullet_i]

                    bullet_inds.append(ind)

            bullet_inds.reverse()
            for b_i in bullet_inds:
                del our_t.bullets[b_i]

            for tank in self.tanks.values():
                inds = []
                for ind, bullet in enumerate(tank.bullets):
                    if not bullet.update():
                        inds.append(ind)

                inds.reverse()
                for ind in inds:
                    del tank.bullets[ind]

                tank.draw()
                for bullet in tank.bullets:
                    bullet.draw()        

            if not self.died.is_set():
                our_t.draw()

            for bullet in our_t.bullets:
                bullet.draw()

            pygame.display.flip()
        
        self.__restart_draw_timer()
        


    def __restart_draw_timer(self):
        self.timed_draw_r = Timer(0.08, self.__worker_draw_and_report)
        self.timed_draw_r.start()