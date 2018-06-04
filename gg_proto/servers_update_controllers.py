import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt

from matplotlib import animation

from math import ceil

import random

class ServersUpdateController:
    def __init__ (self, servers_ids, needed_params=None):
        self.clients = {}
        self.servers_ids = servers_ids
        self.old_conns = {}
        self.max_x = 500
        self.max_y = 600
        self.p_id = 0

        self.colors = ['ro','go', 'bo', 'ko', 'mo', 'co']

        self.old_c = ['yo']

    # decide which server this client should to connect to
    def get_server(self, client_pos, client_id):
        pass

    # update connections if needed
    def update_connections(self):
        pass

    def get_colors(self):
        return self.colors

    def get_configuration(self):
        return self.old_conns
        
    def remove_client(self, id):
        del self.clients[id]

    def plot(self):
        colors =  self.colors

        old_c = self.old_c

        fig = plt.figure(self.p_id)
        self.p_id += 1
        ax = fig.add_subplot(111)
        ax.set_xlim(0, self.max_x)
        ax.set_ylim(0, self.max_y)

        for c_id, client in zip(self.clients.keys(), self.clients.values()):
            x = client['pos'][0]
            y = client['pos'][1]
            plt.plot( x,y , colors[client['s_id']])
            ax.annotate(str(c_id), xy=(x, y))

        fig.show()

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

        self.range = 10

        self.max_x = max_x
        self.max_y = max_y

        self.train_X = self.__split()
    
        self.train_y = self.servers_ids

        print("Train x: {}, train y: {}\n".format( self.train_X, self.train_y))

        self.neigh = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights)

        self.neigh.fit(self.train_X, self.train_y)


    def __split(self):
        n_sections = ceil(self.n_servers/2)

        x = 0
        y = 0

        x_step = self.max_x//n_sections

        train_X = []

        for _ in range(self.n_servers):
            train_X.append([x, y])

            if y == 0:
                y = self.max_y
            else:
                y = 0
                x += x_step

        return train_X

    def get_server(self, client_pos, client_id):
        server_id = self.neigh.predict([client_pos])

        client = {                      \
            'pos'  : client_pos,        \
            's_id' : server_id[0]       \
        }                               \

        self.clients[client_id] = client

        return server_id[0]

    def update_connections(self):

        train_X = []
        train_y = self.servers_ids

        n_clients = []

        for server_id in self.servers_ids:
            p_clients = [x['pos'] for x in self.clients.values() if x['s_id'] == server_id]
            n_clients.append(len(p_clients))

            x_p = [x[0] for x in p_clients]
            y_p = [x[1] for x in p_clients]
            if len(p_clients) is not 0:
                x = sum(x_p)//len(x_p)
                y = sum(y_p)//len(y_p)
                train_X.append([x,y])
            else:
                train_X.append([-1,-1])


        client_connected = [x for x in n_clients if x is not 0] is not []

        if client_connected:
            for c,n in enumerate(n_clients):
                if n is 0:
                    i = n_clients.index(max(n_clients))
                    x = (train_X[i][0] + random.randint(-self.range,self.range)) % self.max_x
                    y = (train_X[i][1] + random.randint(-self.range,self.range)) % self.max_y
                    train_X[c] = [x, y]

        else:
            train_X = self.__split()

        self.old_conns = self.clients
        self.clients = {}

        self.neigh.fit(train_X, train_y)

class KMeansServersUpdate(ServersUpdateController):
    def __init__(self, servers_ids, needed_params):
        super().__init__(servers_ids)
        self.n_servers = len(servers_ids)
        self.train_X = []

        n_clusters = needed_params["n_clusters"]
        random_state = needed_params["random_state"]

        self.random_state = random_state

        max_x = needed_params['max_x']
        max_y = needed_params['max_y']
        
        self.max_x = max_x
        self.max_y = max_y

        self.train_X = self.__split()

        self.train_y = self.servers_ids

        print("Train x: {}, train y: {}\n".format( self.train_X, self.train_y))

        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(self.train_X)


    def __split(self):
        n_sections = ceil(self.n_servers/2)

        x = 0
        y = 0

        x_step = self.max_x//n_sections

        train_X = []

        for _ in range(self.n_servers):
            train_X.append([x, y])

            if y == 0:
                y = self.max_y
            else:
                y = 0
                x += x_step

        return train_X

    def get_server(self, client_pos, client_id):
        server_id = self.kmeans.predict([client_pos])

        client = {                      \
            'pos'  : client_pos,        \
            's_id' : server_id[0]       \
        }                               \

        self.clients[client_id] = client

        return server_id[0]


    def update_connections(self):
        train_X = [x['pos'] for x in self.old_conns.values()]
        train_y = [x['s_id'] for x in self.old_conns.values()]

        train_X += self.train_X
        train_y += self.train_y

        self.old_conns = self.clients
        self.clients = {}

        print("Updating...Train x: {}, train y: {}\n".format( train_X, train_y))
        self.kmeans.fit(train_X, train_y)
