from servers_update_controllers import *

import random

from matplotlib import pyplot as plt

import matplotlib.animation as animation


'''
class ServerUpdatesPlotter:
    def __init__(self, server_updates):
        self.server_updates = server_updates

        self.colors = ['r','g', 'b', 'k', 'm', 'c'] 

    def __animate(self,i):
        clients = self.server_updates.get_configuration()
        plts = ()
        for c_id, client in zip(clients.keys(), clients.values()):
            x = client['pos'][0]
            y = client['pos'][1]
            s_id = client['s_id']
            plts += (x, y, self.colors[s_id % len(self.colors)])
        
        
        animlist = plt.plot(*plts,marker='o', markersize=4)

        for i in range(10):
            self.server_updates.update_connections()

            for c in range(n):
                p = positions[c]
                if p[0] < 150 or p[1] < 200:
                    m = [random.randint(-20,20), random.randint(-20,20)]
                    p[0] = (p[0] + m[0])%500
                    p[1] = (p[1] + m[1])%600
                self.server_updates.get_server(p, c)


        return animlist

        

'''
if __name__ == "__main__":
    
    knn_needed_params = {
        'max_x'       : 500,
        'max_y'       : 600,
        'n_neighbors' : 3,
        'weights'     : 'distance'
    }   

    k_means_needed_params = {
        'max_x'       : 500,
        'max_y'       : 600,
        'n_clusters'  : 4,
        'random_state': None
    }

    servers = [0,1,2,3]

    random_conn = RandomServersUpdate(servers)
    #knn_conn = RandomServersUpdate(servers)
    #knn_conn = KNNServersUpdate(servers, knn_needed_params)
    knn_conn = KMeansServersUpdate(servers, k_means_needed_params)
    knn_conn2 = KNNServersUpdate(servers, knn_needed_params)
    
    move = [[-10,0], [0,-10], [0,10], [10,0]]

    positions2 = [[0, 300], [0, 301], [250, 300], [250, 301], [295, 397], [424, 139], [355, 441], [112, 232], [412, 336], [94, 315], [221, 58], [133, 71], [93, 211], [223, 30], [499, 329], [397, 181], [79, 329], [423, 425], [445, 291], [452, 262], [235, 573], [499, 246], [194, 355], [192, 473], [332, 592], [290, 453], [287, 393], [354, 59], [425, 516], [22, 469], [150, 50], [254, 432], [376, 279], [23, 115], [120, 372], [339, 188], [96, 311], [306, 535], [178, 518], [60, 174], [100, 300], [159, 425], [98, 123], [407, 300], [500, 132], [193, 309], [422, 560], [182, 500], [29, 230], [308, 116], [276, 140], [461, 397], [226, 325], [315, 238], [372, 447], [102, 282], [119, 550], [383, 19], [231, 199], [321, 574], [45, 108], [168, 66], [64, 359], [254, 465], [486, 104], [350, 104], [156, 518], [66, 10], [350, 565], [284, 432], [499, 91], [121, 306], [20, 596], [49, 383], [290, 148], [256, 507], [466, 486], [495, 507], [264, 22], [377, 405], [379, 520], [147, 453], [235, 441], [161, 222], [243, 549], [88, 163], [461, 266], [97, 399], [318, 198], [239, 229], [76, 112], [409, 370], [113, 547], [341, 468], [210, 18], [127, 352], [302, 460], [260, 302], [297, 542], [317, 26], [333, 504], [197, 358], [348, 392], [159, 342]]

    positions = []

    for c in range(len(positions2)//2):
        positions.append( positions2[c])

    fig,ax=plt.subplots()
    ax.set_xlim([0,500])
    ax.set_ylim([0,600])

    ax.grid()


    def init():
        return []


    n = len(positions)

    x = 1
    y = 1

    def animate2(i):
        #print("aa {}".format(n))
        clients = knn_conn.get_configuration()
        #print(clients)
        colors = ['r','g', 'b', 'k', 'm', 'c']
        plts = ()
        for c_id, client in zip(clients.keys(), clients.values()):
            x = client['pos'][0]
            y = client['pos'][1]
            s_id = client['s_id']
            plts += (x, y, colors[s_id % len(colors)])
        
        
        animlist = plt.plot(*plts,marker='o', markersize=4)

        for i in range(10):
            knn_conn.update_connections()

            for c in range(n):
                #print("asdsad----")
                p = positions[c]
                #print(p)
                #if p[0] < 150 or p[1] < 200:
                m = [random.randint(-5,5), random.randint(-5,5)]
                p[0] = (p[0] + m[0])%500
                p[1] = (p[1] + m[1])%600
                knn_conn.get_server(p, c)


        return animlist

  

    for c, pos in enumerate(positions):
        random_conn.get_server(pos, c)
        knn_conn2.get_server(pos, c)

    

    for c in range(n//10):
        knn_conn.get_server(positions[c], c)


    knn_conn.update_connections()

    anim=animation.FuncAnimation(fig,animate2,frames=50,interval=1000,init_func=init,blit=True,repeat=0)
    plt.show()
