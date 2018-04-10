from gg_proto import GGMainServer

from constants import *

def run():
    srv = GGMainServer(prot_id, main_server, servers)

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()