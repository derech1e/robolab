from enums import MessageType, MessageFrom, PathStatus
from typing import Tuple, Self, Dict, Any
from planet import Direction


class PayloadBuilder:
    """
    Class is responsible for building the payload body of a message in the MessageBuilder
    """

    def __init__(self):
        """
        Initializes PayloadBuilder
        """
        self.json = {}

    def planet_name(self, name) -> Self:
        """
        add the planet name to the payload
        :param name: String
        :return: Self
        """
        self.json["planetName"] = name
        return self

    def start_node(self, node: Tuple[Tuple[int, int], Direction]) -> Self:
        """
        add the start node to the payload
        :param node: Tuple[Tuple[int, int], Direction]
        :return: Self
        """
        return self.__start_x(node[0][0]).__start_y(node[0][1]).__start_direction(node[1])

    def end_node(self, node: Tuple[Tuple[int, int], Direction]) -> Self:
        """
        add the end node to the payload
        :param node: Tuple[Tuple[int, int], Direction]
        :return: Self
        """
        return self.__end_x(node[0][0]).__end_y(node[0][1]).__end_direction(node[1])

    def __start_x(self, x_cor: int) -> Self:
        self.json["startX"] = x_cor
        return self

    def __start_y(self, y_cor: int) -> Self:
        self.json["startY"] = y_cor
        return self

    def __end_x(self, x_cor: int) -> Self:
        self.json["endX"] = x_cor
        return self

    def __end_y(self, y_cor: int) -> Self:
        self.json["endY"] = y_cor
        return self

    def __start_direction(self, direction: int) -> Self:
        self.json["startDirection"] = direction
        return self

    def __end_direction(self, direction: int) -> Self:
        self.json["endDirection"] = direction
        return self

    def path_status(self, status: PathStatus) -> Self:
        """
        add a path status to the payload
        :param status: PathStatus
        :return: Self
        """
        self.json["pathStatus"] = status.value
        return self

    def message(self, text: str):
        """
        add a custom message to the payload
        :param text: String
        :return: Self
        """
        self.json["message"] = text
        return self

    def build(self) -> dict[Any, Any]:
        """
        This functions need to be called at the end of the builder. It returns a json object according to the previous used builder pattern
        :return: dict[Any, Any]
        """
        return self.json


class MessageBuilder:
    """
    Class is responsible for building a message send in the communication class.
    """

    def __init__(self):
        """
        Initialize the message builder
        The constructor also sets the "from" attribute of the object to "client"
        """
        self.json = {"from": MessageFrom.CLIENT.value}

    def type(self, message_type: MessageType) -> Self:
        """
        set the message type of the message
        :param message_type: MessageType
        :return: Self
        """
        self.json["type"] = message_type.value
        return self

    def payload(self, payload: PayloadBuilder) -> Self:
        """
        add a payload to the message (see PayloadBuilder for more information)
        :param payload: PayloadBuilder
        :return: Self
        """
        self.json["payload"] = payload
        return self

    def build(self) -> Dict[Any, Any]:
        """
        This functions need to be called at the end of the builder. It returns a json object according to the previous used builder pattern
        :return: dict[Any, Any]
        """
        return self.json
