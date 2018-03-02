#!/usr/bin/python3
import pygame
import sys
import threading

from tank import Tank,Bullet
from controller import Controller, update_screen_event, server_update_event

def main():
    size = width, height = 320, 240
    gray = 112, 112, 112

    server  = ("192.168.0.222", 8080)
    client  = (""         , 0   )
    prot_id = 1

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


    screen = pygame.display.set_mode(size)
    pygame.key.set_repeat(20,20)

    green_tank = pygame.image.load("green_t.png")
    brown_tank = pygame.image.load("brown_t.png")


    game_controller = Controller(screen,
                                 green_tank, 
                                 brown_tank, 
                                 prot_id, 
                                 client, 
                                 server)

    pygame.time.set_timer(update_screen_event, 300)

    game_controller.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit() 
            if (event.type != pygame.KEYDOWN) and \
               (event.type != pygame.KEYUP) and \
               (event.type != server_update_event) and \
               (event.type != update_screen_event): 
                continue
            
            if event.type == update_screen_event:
                game_controller.worker_draw_and_report()
                continue
            
            if event.type == server_update_event:
                print("Updating")
                if event.g_type == "new":
                    game_controller.on_new_user(event.data)
                elif event.g_type == "upd":
                    game_controller.on_user_update(event.data)
                elif event.g_type == "fire":
                    game_controller.on_user_fire(event.data)
                elif event.g_type == "pos":
                    game_controller.on_users_positions(event.data)
                elif event.g_type == "kill":
                    game_controller.on_user_kill_disc(event.data)
                
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
                        game_controller.report_update(keys_movement_x[ev], 0)
                    if ev in keys_movement_y:
                        game_controller.report_update(0, keys_movement_y[ev])
            
            if event.key == pygame.K_SPACE and not keys_down[event.key]:
                game_controller.report_fire()

if __name__ == "__main__":
    main()