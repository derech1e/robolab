#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl
import logging
from typing import Tuple

from builder import MessageBuilder, PayloadBuilder

import paho.mqtt.client as mqtt

from enums import MessageType, MessageFrom, PathStatus
from robot import Robot
import constants
from planet import Direction


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
        self.client.username_pw_set(constants.GROUP_ID, password=constants.PASSWORD)
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)
        self.client.subscribe(f'explorer/{constants.GROUP_ID}', qos=2)
        self.client.loop_start()
        self.logger = logger
        self.syntax_response = {}
        self.robot: Robot = None

        self.debug_path_comparison = {}

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
            self.logger.debug(">>> Not robot instance found!")

        response = json.loads(message.payload.decode('utf-8'))
        msg_type = MessageType(response["type"])
        msg_from = MessageFrom(response["from"])

        if msg_from == MessageFrom.SERVER:
            self.logger.debug(f"Received on topic: {message.topic}")
            payload = response["payload"]

            if msg_type == MessageType.PLANET:
                self.logger.debug("Received planet...")
                self.client.subscribe(f"planet/{payload['planetName']}/{constants.GROUP_ID}")
                self.robot.planet.planet_name = payload['planetName']

                print("*******")
                print(payload["startOrientation"], Direction(payload["startOrientation"]))
                print("*********")

                self.robot.set_start_node(payload["startX"], payload["startY"], Direction(payload["startOrientation"]))

            elif msg_type == MessageType.PATH:
                self.logger.debug("Received current node...")
                start_tuple = ((payload["startX"], payload["startY"]), payload["startDirection"])
                target_tuple = ((payload["endX"], payload["endY"]), payload["endDirection"])

                comp_payload = payload
                #del comp_payload["pathWeight"]

                if self.debug_path_comparison != payload:
                    self.logger.warning(">>> Received path does not match sent path")
                    self.logger.warning("******* SEND PATH ********")
                    self.logger.warning(self.debug_path_comparison)
                    self.logger.warning("******* RECEIVE PATH *********")
                    self.logger.warning(comp_payload)

                self.robot.add_path(start_tuple, target_tuple, payload["pathWeight"])
                self.robot.play_tone()
                self.robot.set_current_node(payload["endX"], payload["endY"], payload["endDirection"])

            elif msg_type == MessageType.PATH_SELECT:
                self.logger.debug(f"Received path select correction...")
                self.robot.update_next_path(payload["startDirection"])

            elif msg_type == MessageType.PATH_UNVEILED:
                start_tuple = ((payload["startX"], payload["startY"]), payload["startDirection"])
                target_tuple = ((payload["endX"], payload["endY"]), payload["endDirection"])
                self.logger.debug(f"Received new unveiled path...")
                self.robot.add_path(start_tuple, target_tuple, payload["pathWeight"])

            elif msg_type == MessageType.TARGET:
                self.logger.debug(f"Received new target...")
                self.robot.set_target((payload["targetX"], payload["targetY"]))

            elif msg_type == MessageType.DONE:
                self.logger.debug("Finished mission")

            self.logger.debug(json.dumps(response, indent=2))
            self.logger.debug("\n\n")

        elif msg_from == MessageFrom.DEBUG:
            if msg_type == MessageType.SYNTAX:
                self.syntax_response = json.dumps(response)

            if msg_type == MessageType.ERROR:
                self.logger.error("******** Communication error *********")
                self.logger.error(json.dumps(response, indent=2))
                self.logger.error("**************************************")

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
        self.logger.debug(json.dumps(message, indent=2) + "\n\n")
        self.client.publish(topic, json.dumps(message), qos=2)

    def send_ready(self) -> None:
        """
        Sends ready message to mother ship
        :return: void
        """
        self.logger.debug("Sending ready...")
        self.send_message(f"explorer/{constants.GROUP_ID}",
                          MessageBuilder()
                          .type(MessageType.READY)
                          .build())

    def send_test_planet(self, planet_name: str) -> None:
        """
        Sends test planet to mother ship
        :param planet_name: String
        :return: void
        """
        self.logger.debug(f"Sending: Test planet...")
        self.send_message(f"explorer/{constants.GROUP_ID}",
                          MessageBuilder()
                          .type(MessageType.TEST_PLANET)
                          .payload(
                              PayloadBuilder()
                              .planet_name(planet_name)
                              .build())
                          .build())

    def send_path(self, planet_name: str, start_node: Tuple[Tuple[int, int], Direction],
                  end_node: Tuple[Tuple[int, int], Direction], path_status: PathStatus) -> None:
        """
        Sends the last driven path to mother ship
        :param planet_name: String
        :param start_node: Tuple[Tuple[int, int], Direction]
        :param end_node: Tuple[Tuple[int, int], Direction]
        :param path_status: PathStatus
        :return: void
        """
        self.debug_path_comparison = MessageBuilder().type(MessageType.PATH).payload(
            PayloadBuilder()
            .start_node(start_node)
            .end_node(end_node)
            .path_status(path_status)
            .build()).build()

        # TODO: REMOVE debug_path_comparison
        self.logger.debug(f"Sending last driven path...")
        self.send_message(f"planet/{planet_name}/{constants.GROUP_ID}", self.debug_path_comparison)

    def send_path_select(self, planet_name: str, node: Tuple[Tuple[int, int], Direction]) -> None:
        """
        Sends the next favoured path to mother ship
        :param planet_name: String
        :param node: Tuple[Tuple[int, int], Direction]
        :return: void
        """
        self.logger.debug("Sending: Path select...")
        self.send_message(f"planet/{planet_name}/{constants.GROUP_ID}",
                          MessageBuilder()
                          .type(MessageType.PATH_SELECT)
                          .payload(
                              PayloadBuilder()
                              .start_node(node)
                              .build())
                          .build())

    def send_target_reached(self, message: str) -> None:
        """
        Sends an information to the mother ship, that the target is reached
        :param message: String
        :return: void
        """
        self.logger.debug("Sending: Target reached...")
        self.send_message(f"explorer/{constants.GROUP_ID}",
                          MessageBuilder()
                          .type(MessageType.TARGET_REACHED)
                          .payload(
                              PayloadBuilder()
                              .message(message)
                              .build())
                          .build())

    def send_exploration_complete(self, message: str) -> None:
        """
        Sends an information to the mother ship, that the planet is explored completely
        :param message: String
        :return: void
        """
        self.logger.debug("Sending: Exploration complete...")
        self.send_message(f"explorer/{constants.GROUP_ID}",
                          MessageBuilder()
                          .type(MessageType.EXPLORATION_COMPLETE)
                          .payload(
                              PayloadBuilder()
                              .message(message)
                              .build())
                          .build())

    def send_com_test(self, message: str) -> None:
        """
        Sends the given message to the mother ship "comtest/003" channel
        :param message: String
        :return: void
        """
        self.send_message(f"comtest/{constants.GROUP_ID}", message)

    def set_robot(self, robot: Robot) -> None:
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
