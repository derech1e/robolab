#!/usr/bin/env python3
import ssl

import ev3dev.ev3 as ev3
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import signal
import json

from communication import Communication
from odometry import Odometry
from planet import Direction, Planet

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client_id = '003-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
    client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                         clean_session=True,  # We want a clean session after disconnect or abort/crash
                         protocol=mqtt.MQTTv311  # Define MQTT protocol version
                         )
    # Setup logging directory and file
    curr_dir = os.path.abspath(os.getcwd())
    if not os.path.exists(curr_dir + '/../logs'):
        os.makedirs(curr_dir + '/../logs')
    log_file = curr_dir + '/../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    print("Hello World!")
    print("Client id: " + client_id)

    def on_message_excepthandler(client, data, message):
        try:
            on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

    # Callback function for receiving messages
    def on_message(client, data, message):
        print('Got message with topic "{}":'.format(message.topic))
        data = json.loads(message.payload.decode('utf-8'))
        print(json.dumps(data, indent=2))
        print("\n")

    client.on_message = on_message_excepthandler
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.username_pw_set('003', password='PYuoI4T4Mv')
    client.connect('mothership.inf.tu-dresden.de', port=8883)
    client.subscribe('explorer/003', qos=2)
    client.loop_start()


    while True:
        user_input = input('Enter disconnect to close the connection...\n')

        if user_input == 'disconnect':
            break

        # you could add some code to send a message here

    client.loop_stop()
    client.disconnect()
    print("Connection closed, program ended!")


# DO NOT EDIT
def signal_handler(sig=None, frame=None, raise_interrupt=True):
    if client and client.is_connected():
        client.disconnect()
    if raise_interrupt:
        raise KeyboardInterrupt()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        run()
        signal_handler(raise_interrupt=False)
    except Exception as e:
        signal_handler(raise_interrupt=False)
        raise e
