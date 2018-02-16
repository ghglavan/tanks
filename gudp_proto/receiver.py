from gudp_proto.gudp_client import Client

def run():
    c = Client(1,"127.0.0.1", 8080, "127.0.0.1", 8082)
    q = c.recv()
    print("q : {}".format(q))

    c.send("saluuut!!:D")

if __name__ == "__main__":
    run()