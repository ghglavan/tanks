from gg_proto import Directions
import pygame


class Bullet:
    COLOR = (96, 53, 0)

    def __init__(self, screen, rect, direction, speed=6):
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
        