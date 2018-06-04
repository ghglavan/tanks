#!/usr/bin/python3
import pygame
import sys
import threading

from tank import Tank,Bullet
from controller import Controller, update_screen_event, server_update_event

from constants import *

from queue import Queue


def main():

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

    pygame.event.set_allowed([
        pygame.QUIT,
        pygame.KEYDOWN,
        pygame.KEYUP,
        server_update_event,
        update_screen_event
    ])

    

    green_tank = pygame.image.load("green_t2.png")
    brown_tank = pygame.image.load("blue_t.png")


    bg = pygame.image.load("bg.png")

    event_q = Queue(EVENT_Q_SIZE)



    game_controller = Controller(screen,
                                 green_tank, 
                                 brown_tank,
                                 bg, 
                                 prot_id, 
                                 client, 
                                 main_server,
                                 event_q,
                                 bullet_dims)

    pygame.time.set_timer(update_screen_event, 300)

    game_controller.start()

    while True:
    
        event = game_controller.get_event()
        if event is None:
            continue

        if event.type == pygame.QUIT: sys.exit() 
        
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

        if event.type != pygame.KEYDOWN and \
           event.type != pygame.KEYUP:
           
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