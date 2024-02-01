from serial import Serial
from time import sleep
from os import system

import pyrebase
import json

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from gpiozero import Servo
import RPi.GPIO as GPIO

PINSERVO = 12
PINZVS = 24

config = json.load(open("./suhuFirebaseConfig.json"))

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
user = auth.sign_in_with_email_and_password("adminkopi@mail.ac.id", "testing123")

print(user)

db = firebase.database()

class AIProccessing :
    def __init__(self) :
        self.__hum = ctrl.Antecedent(np.arange(20, 91, 1), 'hum')
        self.__tmp = ctrl.Antecedent(np.arange(0, 51, 1), 'tmp')
        self.__pre = ctrl.Antecedent(np.arange(900, 1101, 1), 'pre')
        self.__wet = ctrl.Antecedent(np.arange(0, 101, 1), 'wet')
        self.__out = ctrl.Consequent(np.arange(0, 101, 1), 'out')

        self.__membership()
        self.__setRules()

    def __membership(self) :
        self.__hum["low"] = fuzz.trimf(self.__hum.universe, [20, 20, 65])
        self.__hum["medium"] = fuzz.trimf(self.__hum.universe, [20, 60, 80])
        self.__hum["high"] = fuzz.trimf(self.__hum.universe, [75, 90, 90])

        self.__tmp["low"] = fuzz.trimf(self.__tmp.universe, [0, 0, 22])
        self.__tmp["medium"] = fuzz.trimf(self.__tmp.universe, [0, 21, 27])
        self.__tmp["high"] = fuzz.trimf(self.__tmp.universe, [26, 50, 50])

        self.__pre["low"] = fuzz.trimf(self.__pre.universe, [900, 900, 938])
        self.__pre["medium"] = fuzz.trimf(self.__pre.universe, [900, 935, 1011])
        self.__pre["high"] = fuzz.trimf(self.__pre.universe, [1003, 1100, 1100])

        self.__wet["low"] = fuzz.trimf(self.__wet.universe, [0, 0, 50])
        self.__wet["high"] = fuzz.trimf(self.__wet.universe, [45, 100, 100])

        self.__out["low"] = fuzz.trimf(self.__out.universe, [0, 0, 50])
        self.__out["high"] = fuzz.trimf(self.__out.universe, [45, 100, 100])

    def __setRules(self) :
        rules = [
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["low"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["medium"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["low"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["medium"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["low"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["low"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["medium"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["low"], self.__out["high"]),
            ctrl.Rule(self.__hum["high"] & self.__pre["high"] & self.__tmp["high"] & self.__wet["high"], self.__out["low"])
        ]

        boxCtrl = ctrl.ControlSystem(rules)
        self.__boxSim = ctrl.ControlSystemSimulation(boxCtrl)

    def AICompute(self, dataDICT) :
        self.__boxSim.input['hum'] = dataDICT["hum"]
        self.__boxSim.input['tmp'] = dataDICT["tmp"]
        self.__boxSim.input['pre'] = dataDICT["pre"]
        self.__boxSim.input['wet'] = dataDICT["wet"]

        self.__boxSim.compute()

        return round(self.__boxSim.output['out'], 2)


if __name__ == "__main__" :
    callAI = AIProccessing()
    servo = Servo(PINSERVO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINZVS, GPIO.OUT)

    serial = Serial('/dev/ttyACM0', 9600, timeout=1)
    serial.reset_input_buffer()

    try :
        while True :
            system("clear")
            serial.write(b"OK\n")
            if serial.in_waiting > 0:
                line = serial.readline().decode('utf-8').rstrip()
                dataRAW = line.split(",")
                dataFINAL = {}
                dataFINAL["tmp"] = 0

                for i in range(len(dataRAW)) :
                    temp = dataRAW[i].split(":")
                    if temp[0] == "tmpBMP" or temp[0] == "tmpDHT" :
                        dataFINAL["tmp"] += float(temp[1])
                    elif temp[0] == "pre" :
                        dataFINAL[temp[0]] = round(float(temp[1]) / 100, 2)
                    elif temp[0] == "wet" :
                        dataFINAL[temp[0]] = round((float(temp[1]) / 1023) * 100.00, 2)
                    else :
                        dataFINAL[temp[0]] = round(float(temp[1]), 2)
                dataFINAL["tmp"] = round(float(dataFINAL["tmp"]) / 2, 2)
                dataFINAL["fuzz"] = callAI.AICompute(dataFINAL)

                if dataFINAL["fuzz"] < 50.00 :
                    servo.min()
                    GPIO.output(PINZVS, 0)
                else :
                    servo.max()
                    GPIO.output(PINZVS, 1)

                db.child(user["localId"]).set(dataFINAL)

                print(dataRAW)
                print("")
                print(dataFINAL)

                sleep(0.5)
    except Exception as error:
        servo.close()
        GPIO.cleanup()
        serial.close()
        print(error)
