from gudp_server import Server
from time import sleep

def run():
    s = Server(1, "127.0.0.1", 8082)
    s.send_to("Hello!!:D", ("127.0.0.1", 8080))
    q = s.recv()
    print("q: {}".format(q))


if __name__ == "__main__":
    run()