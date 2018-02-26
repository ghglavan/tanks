from gg_proto import GGServer

def run():
    srv = GGServer(1,("127.0.0.1", 8080))

    srv.start()
    srv.join()

if __name__ == "__main__":
    run()