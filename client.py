from gg_proto import GGClient

def run():
    client = GGClient(1, ("127.0.0.1", 8081), ("127.0.0.1", 8080))

    client.connect()

    while not client.is_id_set():
        continue

    print("Got id: {}".format(client.id))


if __name__ == "__main__":
    run()