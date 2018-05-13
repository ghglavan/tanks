import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from servers_update_controllers import KNNServersUpdate, RandomServersUpdate, KMeansServersUpdate
import pytest

def test_knn_update_get():
    needed_params = {
        'max_x'       : 500,
        'max_y'       : 600,
        'n_neighbors' : 3,
        'weights'     : 'distance'
    }
    controller = KNNServersUpdate([0,1,2,3], needed_params)

    assert(controller.get_server([0,300], 0) == 0)
    assert(controller.get_server([0,301], 0) == 1)
    assert(controller.get_server([250,300], 0) == 2)
    assert(controller.get_server([250,301], 0) == 3)

    controller.update_connections()

@pytest.mark.parametrize("n_clients", [4, 5, 6 ,7 ,8])
def test_random_get(n_clients):
    servers = [0,1,2,3]
    n_servers = len(servers)

    controller = RandomServersUpdate(servers)

    for n_c in range(n_clients):
        assert(controller.get_server([0,n_c], n_c) == n_c % n_servers)


def test_kmeans_update_get():
    needed_params = {
        'max_x'       : 500,
        'max_y'       : 600,
        'n_clusters'  : 4,
        'random_state': 2
    }
    controller = KMeansServersUpdate([0,1,2,3], needed_params)

    assert(controller.get_server([0,300], 0)[0] == 0)
    assert(controller.get_server([0,301], 0)[0] == 1)
    assert(controller.get_server([250,300], 0)[0] == 2)
    assert(controller.get_server([250,301], 0)[0] == 3)

    controller.update_connections()