import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans

from math import ceil

class ServersUpdateController:
    def __init__ (self, servers_ids, needed_params=None):
        self.clients = {}
        self.servers_ids = servers_ids

    # decide which server this client should to connect to
    def get_server(self, client_pos, client_id):
        pass

    # update connections if needed
    def update_connections(self):
        pass

    def get_configuration(self):
        return self.clients

    def remove_client(self, id):
        del self.clients[id]


class RandomServersUpdate(ServersUpdateController):
    def __init__(self, servers_ids):
        super().__init__(servers_ids)
        self.n_servers = len(servers_ids)
        self.last_server = 0

    def get_server(self, client_pos, client_id):
        
        server_id = self.servers_ids[self.last_server]
        
        client = {                      \
            'pos'  : client_pos,        \
            's_id' : server_id          \
        }                               \

        self.clients[client_id] = client

        self.last_server = (self.last_server + 1) % self.n_servers

        return server_id
        

    def update_connections(self):
        pass



class KNNServersUpdate(ServersUpdateController):
    def __init__(self, servers_ids, needed_params):
        super().__init__(servers_ids)
        self.n_servers = len(servers_ids)
        self.train_X = []

        n_neighbors = needed_params['n_neighbors']
        weights = needed_params['weights']

        max_x = needed_params['max_x']
        max_y = needed_params['max_y']
        x = 0
        y = 0

        n_sections = ceil(self.n_servers/2)

        x_step = max_x//n_sections

        for _ in range(self.n_servers):
            self.train_X.append([x, y])

            if y == 0:
                y = max_y
            else:
                y = 0
                x += x_step
    
        self.train_y = self.servers_ids

        print("Train x: {}, train y: {}\n".format( self.train_X, self.train_y))

        self.neigh = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights)

        self.neigh.fit(self.train_X, self.train_y)


    def get_server(self, client_pos, client_id):
        server_id = self.neigh.predict([client_pos])

        client = {                      \
            'pos'  : client_pos,        \
            's_id' : server_id[0]       \
        }                               \

        self.clients[client_id] = client

        return server_id

    def update_connections(self):
        train_X = [x['pos'] for x in self.clients.values()]
        train_y = [x['s_id'] for x in self.clients.values()]

        train_X += self.train_X
        train_y += self.train_y

        self.clients = []

        print("Updating...Train x: {}, train y: {}\n".format( train_X, train_y))
        self.neigh.fit(train_X, train_y)

class KMeansServersUpdate(ServersUpdateController):
    def __init__(self, servers_ids, needed_params):
        super().__init__(servers_ids)
        self.n_servers = len(servers_ids)
        self.train_X = []

        n_clusters = needed_params["n_clusters"]
        random_state = needed_params["random_state"]

        max_x = needed_params['max_x']
        max_y = needed_params['max_y']
        x = 0
        y = 0

        n_sections = ceil(self.n_servers/2)

        x_step = max_x//n_sections

        for _ in range(self.n_servers):
            self.train_X.append([x, y])

            if y == 0:
                y = max_y
            else:
                y = 0
                x += x_step
    
        self.train_y = self.servers_ids

        print("Train x: {}, train y: {}\n".format( self.train_X, self.train_y))

        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(self.train_X)
        
    def get_server(self, client_pos, client_id):
        server_id = self.kmeans.predict([client_pos])

        client = {                      \
            'pos'  : client_pos,        \
            's_id' : server_id[0]       \
        }                               \

        self.clients[client_id] = client

        return server_id


    def update_connections(self):
        train_X = [x['pos'] for x in self.clients.values()]
        train_y = [x['s_id'] for x in self.clients.values()]

        train_X += self.train_X
        train_y += self.train_y

        self.clients = []

        print("Updating...Train x: {}, train y: {}\n".format( train_X, train_y))
        self.kmeans.fit(train_X, train_y)
