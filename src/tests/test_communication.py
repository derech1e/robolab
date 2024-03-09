#!/usr/bin/env python3
import json
import time
import unittest.mock
import paho.mqtt.client as mqtt
import uuid

from communication import Communication
from builder import MessageBuilder, PayloadBuilder
from enums import MessageType, PathStatus

"""
IMPORTANT: THOSE TESTS ARE NOT REQUIRED FOR THE EXAM AND USED ONLY FOR DEVELOPMENT
ASK YOUR TUTOR FOR SPECIFIC DETAILS ABOUT THIS!
"""


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = '003-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)
        self.communication.client.subscribe('comtest/003')
        self.CORRECT_SYNTAX = {'from': 'debug', 'type': 'syntax', 'payload': {'message': 'Correct'}}

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        self.communication.send_com_test(
            MessageBuilder()
            .type(MessageType.READY)
            .build())
        time.sleep(0.2)
        self.assertEqual(self.communication.syntax_response, json.dumps(self.CORRECT_SYNTAX))

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        self.communication.send_com_test(
            MessageBuilder()
            .type(MessageType.PATH)
            .payload(
                PayloadBuilder()
                .start_x(0)
                .start_y(0)
                .start_direction(0)
                .end_x(0)
                .end_y(0)
                .end_direction(0)
                .path_status(PathStatus.FREE)
                .build())
            .build())
        time.sleep(0.2)
        self.assertEqual(self.communication.syntax_response, json.dumps(self.CORRECT_SYNTAX))

    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        self.communication.send_com_test(
            MessageBuilder()
                          .type(MessageType.PATH)
                          .payload(
                              PayloadBuilder()
                              .start_x(0)
                              .start_y(0)
                              .start_direction("asd")
                              .end_x(0)
                              .end_y(0)
                              .end_direction(0)
                              .path_status(PathStatus.FREE)
                              .build())
                          .build())
        time.sleep(0.2)
        self.assertNotEqual(self.communication.syntax_response, json.dumps(self.CORRECT_SYNTAX))

    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        self.communication.send_com_test(
            MessageBuilder()
            .type(MessageType.PATH_SELECT)
            .payload(
                PayloadBuilder()
                .start_x(0)
                .start_y(0)
                .start_direction(0)
                .build())
            .build())
        time.sleep(0.2)
        self.assertEqual(self.communication.syntax_response, json.dumps(self.CORRECT_SYNTAX))

    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        self.communication.send_com_test(
            MessageBuilder()
            .type(MessageType.EXPLORATION_COMPLETE)
            .payload(
                PayloadBuilder()
                .message("")
                .build())
            .build())
        time.sleep(0.2)
        self.assertEqual(self.communication.syntax_response, json.dumps(self.CORRECT_SYNTAX))


if __name__ == "__main__":
    unittest.main()
