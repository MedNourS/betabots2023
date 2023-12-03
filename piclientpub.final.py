from os.path import basename
import logging
import time
import ntcore

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Initialize NT4 client
    inst = ntcore.NetworkTableInstance.getDefault()

    inst.startClient4("raspyPi")

    inst.setServer("192.168.0.21") #! Change IP with server's IP

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