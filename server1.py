from gg_proto import GGServer

from constants import *

def run():
    srv = GGServer(prot_id, servers[0], main_server)

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()