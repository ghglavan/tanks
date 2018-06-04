from gg_proto import GGMainServer, KNNServersUpdate

from constants import *

def run():

    server_params = {
        "width": width,
        "height": height,
        "u_interval": update_interval,
        "d_tank": 10
    }

    knn_needed_params = {
        'max_x'       : width,
        'max_y'       : height,
        'n_neighbors' : 2,
        'weights'     : 'distance'
    } 

    knn_con = KNNServersUpdate(servers_ids, knn_needed_params)

    srv = GGMainServer(prot_id, main_server, servers, server_params, positions, knn_con)

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()