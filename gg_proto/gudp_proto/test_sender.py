from gudp_server import Server
from time import sleep

def run():
    s = Server(1, "127.0.0.1", 8082)
    s.send_to("Hello!!:D".encode(), ("127.0.0.1", 8080))
    sleep(1000)


if __name__ == "__main__":
    run()