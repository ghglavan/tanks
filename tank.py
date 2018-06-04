import pygame
from gg_proto import Directions
from bullet import Bullet
from time import time

class Tank:
    
    def __init__    (self,
                    t_id, 
                    image, 
                    screen,
                    bullet_dimentions,
                    tank_position=[0,0],
                    gun_o = Directions.UP, 
                    bullet_speed=5,
                    speed=1):

        self.rect = image.get_rect()
        self.rect = self.rect.move(tank_position)

        self.local_rect = self.rect.copy()

        self.id = t_id

        self.image = image
        self.screen = screen
        self.w_width = screen.get_width()
        self.w_height = screen.get_height()
        self.speed = speed
        self.gun_o = gun_o
        self.rotate(Directions.UP, gun_o)

        self.local_go = gun_o

        self.bullet_dimentions = bullet_dimentions

        self.bullets = []
        self.last_update        = None
        self.last_local_update  = None
        self.last_fired         = None

    def get_gun_dir(self):
        return self.gun_o

    def rotate(self, from_p, to_p):
        print("Roatating from {}, to {}".format(Directions(from_p), Directions(to_p)))
        self.image = pygame.transform.rotate(self.image, (int(to_p)-int(from_p)) * 90)

    def get_rect(self):
        return self.rect

    def update_o(self, o):
        self.rotate(self.gun_o, o)
        self.gun_o = o
        

    def get_pos(self):
        return (self.rect.x, self.rect.y, self.gun_o)

    def get_local_pos(self, l_u=None):
        if l_u:
            self.last_local_update = l_u    
        else:
            self.last_local_update = time()
        return (self.local_rect.x, self.local_rect.y, self.local_go)

    def move(self, where, u_ts = None):
        if u_ts is not None:
            self.last_update = u_ts
        else:
            self.last_update = time()

        if where[0] != 0:
            self.__move_x(where[0])
        if where[1] != 0:
            self.__move_y(where[1])

    def s_move(self, where, l_u = None):
        if l_u:
            self.last_local_update = l_u    
        else:
            self.last_local_update = time()

        if where[0] != 0:
            return self.__s_move_x(where[0])
        if where[1] != 0:
            return self.__s_move_y(where[1])

    def __s_move_x(self, where):
        x, y = self.local_rect.topleft
        gun_o = self.local_go

        x += where * self.speed
        if where == -1 and self.local_go != Directions.LEFT:
            gun_o = Directions.LEFT
        if where == 1 and self.local_go != Directions.RIGHT:
            gun_o = Directions.RIGHT

        if x < 0 or x + self.local_rect.width > self.w_width:
            x -= where * self.speed

        self.local_go = gun_o
        self.local_rect.x = x
        self.local_rect.y = y

        return (x, y, gun_o)

    def __s_move_y(self, where):
        x, y = self.local_rect.topleft
        gun_o = self.local_go

        y += where * self.speed

        if where == -1 and self.local_go != Directions.UP:
            gun_o = Directions.UP
        if where == 1 and self.local_go != Directions.DOWN:
            gun_o = Directions.DOWN
        
        if y < 0 or y + self.local_rect.height > self.w_height:
            y -= where * self.speed


        self.local_go = gun_o
        self.local_rect.x = x
        self.local_rect.y = y

        return (x, y, gun_o)

    def __move_x(self, where):
        self.rect = self.rect.move([where * self.speed, 0])
        if where == -1 and self.gun_o != Directions.LEFT:
            self.rotate(self.gun_o, Directions.LEFT)
            self.gun_o = Directions.LEFT
        if where == 1 and self.gun_o != Directions.RIGHT:
            self.rotate(self.gun_o, Directions.RIGHT)
            self.gun_o = Directions.RIGHT
        if self.rect.left < 0 or self.rect.right > self.w_width:
            self.rect = self.rect.move([-where * self.speed,0])

    def __move_y(self, where):
        self.rect = self.rect.move([0, where * self.speed])
        if where == -1 and self.gun_o != Directions.UP:
            self.rotate(self.gun_o, Directions.UP)
            self.gun_o = Directions.UP
        if where == 1 and self.gun_o != Directions.DOWN:
            self.rotate(self.gun_o, Directions.DOWN)
            self.gun_o = Directions.DOWN
        if self.rect.top < 0 or self.rect.bottom > self.w_height:
            self.rect = self.rect.move([0, -where * self.speed])

    def draw(self):
        try:
            self.screen.blit(self.image, self.rect)
        except:
            print("Exception blitting")
            return

    def fire(self, f_ts=None):
        if f_ts is not None:
            self.last_fired = f_ts
        else:
            self.last_fired = time()

        bullet_coords = (0,0)
        if self.gun_o == Directions.UP:
            bullet_coords = (self.rect.midtop[0]-1, self.rect.midtop[1]-1-self.bullet_dimentions[1]) 
        elif self.gun_o == Directions.DOWN:
            bullet_coords = (self.rect.midbottom[0]-1, self.rect.midbottom[1]+1)
        elif self.gun_o == Directions.LEFT:
            bullet_coords = (self.rect.midleft[0]-1-self.bullet_dimentions[0], self.rect.midleft[1]-1)
        else:
            bullet_coords = (self.rect.midright[0]+1, self.rect.midright[1]-1)

        self.bullets.append(Bullet(
            self.screen, 
            pygame.Rect(bullet_coords, self.bullet_dimentions),
            self.gun_o
            ))
