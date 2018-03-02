from gg_proto import GGServer

def run():
    srv = GGServer(1,("192.168.0.222", 8080))

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()