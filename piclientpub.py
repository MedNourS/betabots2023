import argparse
import os
from os.path import basename
import logging
import time
import ntcore

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, help="IP address to connect to")
    args = parser.parse_args()

    # Initialize NT4 client
    inst = ntcore.NetworkTableInstance.getDefault()

    identity = f"{basename(__file__)}-{os.getpid()}"
    inst.startClient4(identity)

    inst.setServer(args.ip)

    # publish two values
    table = inst.getTable("values")
    publish = table.getFloatArrayTopic("idexidy").publish()

    id = 7
    x = 167
    y = 436
    distance = 3.14
    yaw = 90.124
    i = 0
    while True:

        publish.set([id, x, y, distance, yaw, i])

        time.sleep(0.5)

        i += 1