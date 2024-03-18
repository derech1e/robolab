from enums import MessageType, MessageFrom, PathStatus
from typing import Tuple
from planet import Direction


class PayloadBuilder:

    def __init__(self):
        self.json = {}

    def planet_name(self, name):
        self.json["planetName"] = name
        return self

    def start_node(self, node: Tuple[Tuple[int, int], Direction]):
        return self.__start_x(node[0][0]).__start_y(node[0][1]).__start_direction(node[1])

    def end_node(self, node: Tuple[Tuple[int, int], Direction]):
        return self.__end_x(node[0][0]).__end_y(node[0][1]).__end_direction(node[1])

    def __start_x(self, x_cor: int):
        self.json["startX"] = x_cor
        return self

    def __start_y(self, y_cor: int):
        self.json["startY"] = y_cor
        return self

    def __end_x(self, x_cor: int):
        self.json["endX"] = x_cor
        return self

    def __end_y(self, y_cor: int):
        self.json["endY"] = y_cor
        return self

    def __start_direction(self, direction: int):
        self.json["startDirection"] = direction
        return self

    def __end_direction(self, direction: int):
        self.json["endDirection"] = direction
        return self

    def path_status(self, status: PathStatus):
        self.json["pathStatus"] = status.value
        return self

    def message(self, text: str):
        self.json["message"] = text
        return self

    def build(self):
        return self.json


class MessageBuilder:

    def __init__(self):
        self.json = {"from": MessageFrom.CLIENT.value}

    def type(self, message_type: MessageType):
        self.json["type"] = message_type.value
        return self

    def payload(self, payload: PayloadBuilder):
        self.json["payload"] = payload
        return self

    def build(self):
        return self.json
