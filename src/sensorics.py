import ev3dev.ev3 as ev3
import json


class Sensors:
    def __init__(self):
        self.cs = ev3.ColorSensor()
        self.cs.mode = "RGB-RAW"
        self.colorData = {"white": (0,0,0), "black": (0,0,0), "blue": (0,0,0), "red": (0,0,0,0)}

        # set the range in which the read value is accepted as a color
        self.acceptenceRange = (10,10,10)

    # retruns the color read by the sensor (R,G,B) 1020
    def getColor(self): #->tuple[int,int,int]
        return self.cs.raw

    def checkColor(self):
        #TODO: schoener machen evtl anderer farbraum
        rawColor = self.cs.raw

        value = self.colorData["blue"]
        if rawColor[0] > value[0] - self.acceptenceRange[0] and rawColor[0] < value[0] + self.acceptenceRange[0]:
            if rawColor[1] > value[1] - self.acceptenceRange[1] and rawColor[1] < value[1] + self.acceptenceRange[1]:
                if rawColor[2] > value[2] - self.acceptenceRange[2] and rawColor[2] < value[2] + self.acceptenceRange[2]:
                    return "blue"

        value = self.colorData["red"]
        if rawColor[0] > value[0] - self.acceptenceRange[0] and rawColor[0] < value[0] + self.acceptenceRange[0]:
            if rawColor[1] > value[1] - self.acceptenceRange[1] and rawColor[1] < value[1] + self.acceptenceRange[1]:
                if rawColor[2] > value[2] - self.acceptenceRange[2] and rawColor[2] < value[2] + self.acceptenceRange[2]:
                    return "red"
        return False
        

    # read color Data from file
    def loadColorData(self):
        with open("resources/colorData.json", "r") as data:
            self.colorData = json.load(data)

    # save color Data to file
    def calibrate(self):
        # read white, read black, read blue, read red
        print("calibrating...")
        
        for color, value in self.colorData.items():
            input(f'put the rover on {color}')
            self.colorData[color] = self.getColor()

        with open("resources/colorData.json", "w") as data:
            json.dump(self.colorData, data)

        print("calibration completed")
