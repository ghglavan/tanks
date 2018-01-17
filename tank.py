import pygame
import directions as Directions

class Tank:
    
    def __init__    (self, 
                    image, 
                    screen,
                    bullet_dimentions,
                    bullet_speed=1, 
                    speed=1):
        

        self.rect = image.get_rect()
        self.image = image
        self.screen = screen
        self.w_width = screen.get_width()
        self.w_height = screen.get_height()
        self.speed = speed
        self.gun_o = Directions.UP
        self.bullet_dimentions = bullet_dimentions

    def get_gun_dir(self):
        return self.gun_o

    def rotate(self, from_p, to_p):
        self.image = pygame.transform.rotate(self.image, (to_p-from_p) * 90)

    def get_rect(self):
        return self.rect

    def move_x(self, where):
        self.rect = self.rect.move([where * self.speed, 0])
        if where == -1 and self.gun_o != Directions.LEFT:
            self.rotate(self.gun_o, Directions.LEFT)
            self.gun_o = Directions.LEFT
        if where == 1 and self.gun_o != Directions.RIGHT:
            self.rotate(self.gun_o, Directions.RIGHT)
            self.gun_o = Directions.RIGHT
        if self.rect.left < 0 or self.rect.right > self.w_width:
            self.rect = self.rect.move([-where * self.speed,0])

    def move_y(self, where):
        if where == -1 and self.gun_o != Directions.UP:
            self.rotate(self.gun_o, Directions.UP)
            self.gun_o = Directions.UP
        if where == 1 and self.gun_o != Directions.DOWN:
            self.rotate(self.gun_o, Directions.DOWN)
            self.gun_o = Directions.DOWN
        self.rect = self.rect.move([0, where * self.speed])
        if self.rect.top < 0 or self.rect.bottom > self.w_height:
            self.rect = self.rect.move([0, -where * self.speed])

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def fire(self):
        bullet_coords = (0,0)
        if self.gun_o == Directions.UP:
            bullet_coords = (self.rect.midtop[0]-1, self.rect.midtop[1]-1-self.bullet_dimentions[1]) 
        elif self.gun_o == Directions.DOWN:
            bullet_coords = (self.rect.midbottom[0]-1, self.rect.midbottom[1]+1)
        elif self.gun_o == Directions.LEFT:
            bullet_coords = (self.rect.midleft[0]-1-self.bullet_dimentions[0], self.rect.midleft[1]-1)
        else:
            bullet_coords = (self.rect.midright[0]+1, self.rect.midright[1]-1)

        return Bullet(
            self.screen, 
            pygame.Rect(bullet_coords, self.bullet_dimentions),
            self.gun_o
            )

class Bullet:
    COLOR = (96, 53, 0)

    def __init__(self, screen, rect, direction, speed=1):
        self.screen = screen
        self.rect = rect
        self.direction = direction
        self.speed = speed

    def draw(self):
        pygame.draw.rect(self.screen, self.COLOR, self.rect)

    def get_rect(self):
        return self.rect

    def update(self):
        if self.direction == Directions.UP:
            self.rect = self.rect.move(0, -self.speed)
        elif self.direction == Directions.DOWN:
            self.rect = self.rect.move(0, self.speed)
        elif self.direction == Directions.LEFT:
            self.rect = self.rect.move(-self.speed, 0)
        else:
            self.rect = self.rect.move(self.speed, 0)

        return self.screen.get_rect().contains(self.rect)
        