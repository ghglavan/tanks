from dummy_controller import DummyController

from constants import *

from time import sleep

if __name__ == "__main__":
    
    controllers = []

    for i in range(16):
        controller = DummyController(prot_id, client, main_server)
        controller.start()
        controllers.append(controller)
        print("controller {} connected".format(i))


    cl = 15

    for controller in controllers:
        if controller.server != controllers[cl].server:
            print("sending kill to another server")
            controllers[cl].report_kill(controller.id)
            break

    start, end = controllers[cl].get_kill_interval()
    print ("k_rep at {}, response at {}, time {}".format(start, end, end-start))

    sleep(end-start)

    for controller in controllers:
        if controller.server == controllers[cl].server:
            print("sending kill to another server")
            controllers[cl].report_kill(controller.id)
            break

    start, end = controllers[cl].get_kill_interval()
    print ("k_rep at {}, response at {}, time {}".format(start, end, end-start))
    


    sleep(10000)

    