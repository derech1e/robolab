#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
from enum import Enum
import logging
from builder import MessageBuilder, PayloadBuilder

import paho.mqtt.client as mqtt

from enums import MessageType, MessageFrom, PathStatus
from robot import Robot

GROUP = "003"


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    # DO NOT EDIT THE METHOD SIGNATURE
    def __init__(self, mqtt_client: mqtt.Client, logger: logging.Logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        self.client.username_pw_set('003', password='PYuoI4T4Mv')
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)
        self.client.subscribe('explorer/003', qos=2)
        self.client.loop_start()
        self.logger = logger
        self.syntax_response = {}
        self.robot: Robot = None

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """

        if self.robot is None:
            self.logger.warning("Not robot instance found!")

        response = json.loads(message.payload.decode('utf-8'))
        msg_type = MessageType(response["type"])
        msg_from = MessageFrom(response["from"])

        if msg_from == MessageFrom.SERVER:
            self.logger.debug(f"Received on topic: {message.topic}")
            self.logger.debug(json.dumps(response, indent=2))

            payload = response["payload"]

            if msg_type == MessageType.PLANET:
                self.logger.debug("Received planet")
                self.client.subscribe(f"planet/{payload['planetName']}")
                # TODO: set startX, startY and startOrientation on planet
            elif msg_type == MessageType.PATH:
                self.logger.debug("Received current path")
                start_tuple = ((payload["startX"], payload["startY"]), payload["startDirection"])
                target_tuple = ((payload["endX"], payload["endY"]), payload["endDirection"])
                self.robot.add_path(start_tuple, target_tuple, payload["pathWeight"])
                self.robot.play_tone()
                # TODO: Impl logic for pathStatus 'free|blocked‘
            elif msg_type == MessageType.PATH_SELECT:
                self.logger.debug("Received new path")
                self.robot.update_target_direction(payload["startDirection"])
            elif msg_type == MessageType.PATH_UNVEILED:
                self.logger.debug("Received unveiled path")
                start_tuple = ((payload["startX"], payload["startY"]), payload["startDirection"])
                target_tuple = ((payload["endX"], payload["endY"]), payload["endDirection"])
                self.robot.add_path(start_tuple, target_tuple, payload["pathWeight"])
                # TODO: Check if just add_path works !!
            elif msg_type == MessageType.TARGET:
                self.logger.debug("Received target")
                self.robot.set_current_target((payload["targetX"], payload["targetY"]))
            elif msg_type == MessageType.DONE:
                self.logger.debug("Finished mission")

        elif msg_from == MessageFrom.DEBUG:
            if msg_type == MessageType.SYNTAX:
                self.syntax_response = json.dumps(response)

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))
        self.client.publish(topic, json.dumps(message), qos=2)

        # TODO: Impl syntax checker

    def send_ready(self):
        self.send_message(f"explorer/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.READY)
                          .build())

    def send_test_planet(self, planet_name: str):
        self.send_message(f"explorer/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.TEST_PLANET)
                          .payload(
                              PayloadBuilder()
                              .planet_name(planet_name)
                              .build())
                          .build())

    def send_path(self, planet: str, start_x: int, start_y: int, start_direction: int, end_x: int, end_y: int,
                  end_direction: int, path_status: PathStatus):
        self.send_message(f"planet/{planet}/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.PATH)
                          .payload(
                              PayloadBuilder()
                              .start_x(start_x)
                              .start_y(start_y)
                              .start_direction(start_direction)
                              .end_x(end_x)
                              .end_y(end_y)
                              .end_direction(end_direction)
                              .path_status(path_status)
                              .build())
                          .build())

    def send_path_select(self, planet: str, start_x: int, start_y: int, start_direction: int):
        self.send_message(f"planet/{planet}/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.PATH_SELECT)
                          .payload(
                              PayloadBuilder()
                              .start_x(start_x)
                              .start_y(start_y)
                              .start_direction(start_direction)
                              .build())
                          .build())

    def send_target_reached(self, message: str):
        self.send_message(f"explorer/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.TARGET_REACHED)
                          .payload(
                              PayloadBuilder()
                              .message(message)
                              .build())
                          .build())

    def send_exploration_complete(self, message: str):
        self.send_message(f"explorer/{GROUP}",
                          MessageBuilder()
                          .type(MessageType.EXPLORATION_COMPLETE)
                          .payload(
                              PayloadBuilder()
                              .message(message)
                              .build())
                          .build())

    def send_com_test(self, message: str):
        self.send_message(f"comtest/{GROUP}", message)

    def set_robot(self, robot: Robot):
        self.robot = robot

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise
