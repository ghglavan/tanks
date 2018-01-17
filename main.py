#!/usr/bin/python3
import pygame
import sys
import threading

from tank import Tank,Bullet

def test(bullet):
    return bullet.update()

def update_bullets(bullets, tanks):
    print("Updating: {}".format(len(bullets)))
    bullets_ins = []
    tanks_ins = []
    for ind, bullet in enumerate(bullets):
        collided = False
        for i,tank in enumerate(tanks):
            if bullet.get_rect().colliderect(tank.get_rect()):
                bullets_ins.append(ind)
                tanks_ins.append(i)
                collided = True
                break
        
        if collided:
            continue

        if not test(bullet):
            bullets_ins.append(ind)
    
    for ind in bullets_ins:
        del bullets[ind]

    for ind in tanks_ins:
        del tanks[ind]

    threading.Timer(0.02, update_bullets, [bullets, tanks]).start()


def main():
    size = width, height = 320, 240
    gray = 112, 112, 112

    keys_down = {
        pygame.K_SPACE : False, 
        pygame.K_UP    : False, 
        pygame.K_DOWN  : False,    
        pygame.K_RIGHT : False, 
        pygame.K_LEFT  : False
    }

    keys_movement_x = {
        pygame.K_LEFT   : -1,
        pygame.K_RIGHT  : 1,
    }

    keys_movement_y = {
        pygame.K_UP     : -1,
        pygame.K_DOWN   : 1,
    }

    is_space_down = False
    
    tanks = []
    bullets = []
    update_bullets(bullets, tanks)

    bullet_rect_dimentions = (3,3)

    screen = pygame.display.set_mode(size)
    pygame.key.set_repeat(20,20)

    green_tank = pygame.image.load("green_t.png")
    brown_tank = pygame.image.load("brown_t.png")    
    g_tank = Tank(green_tank, screen, bullet_rect_dimentions)
    b_tank = Tank(brown_tank, screen, bullet_rect_dimentions)

    tanks.append(g_tank)
    tanks.append(b_tank)

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if (event.type != pygame.KEYDOWN) and \
               (event.type != pygame.KEYUP): 
                continue
            
            if event.key not in keys_down:
                continue
            
            if event.type == pygame.KEYDOWN:
                keys_down[event.key] = True
            
            if event.type == pygame.KEYUP:
                keys_down[event.key] = False


            for ev,bo in keys_down.items():
                if bo:
                    if ev in keys_movement_x:
                        g_tank.move_x(keys_movement_x[ev])
                    if ev in keys_movement_y:
                        g_tank.move_y(keys_movement_y[ev])
            
            if event.key == pygame.K_SPACE and not keys_down[event.key]:
                bullets.append(g_tank.fire())

        screen.fill(gray)

        for tank in tanks:
            tank.draw()

        for bullet in bullets:
            bullet.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()