from gg_proto import GGMainServer, KMeansServersUpdate

from constants import *

def run():

    server_params = {
        "width": width,
        "height": height,
        "u_interval": update_interval,
        "d_tank": 10
    }

    k_means_needed_params = {
        'max_x'       : 500,
        'max_y'       : 600,
        'n_clusters'  : 2,
        'random_state': 2345
    }

    knn_con = KMeansServersUpdate(servers_ids, k_means_needed_params)

    srv = GGMainServer(prot_id, main_server, servers, server_params, positions, knn_con)

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()