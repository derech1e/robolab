from enums import MessageType, MessageFrom, PathStatus


class PayloadBuilder:

    def __init__(self):
        self.json = {}

    def planet_name(self, name):
        self.json["planetName"] = name
        return self

    def start_x(self, x_cor: int):
        self.json["startX"] = x_cor
        return self

    def start_y(self, y_cor: int):
        self.json["startY"] = y_cor
        return self

    def end_x(self, x_cor: int):
        self.json["endX"] = x_cor
        return self

    def end_y(self, y_cor: int):
        self.json["endY"] = y_cor
        return self

    def start_direction(self, direction: int):
        self.json["startDirection"] = direction
        return self

    def end_direction(self, direction: int):
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
