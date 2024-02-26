import json
import os
from mcf_data import SCORE_TRACE_PATH
from global_data import Validator

class Trace:

    tracing_game = ''
    # result: dict = {}
    def get_json():
        with open(SCORE_TRACE_PATH, 'r') as file:
            return json.load(file)
    
    def put_to_json(data):
        with open(SCORE_TRACE_PATH, 'w+') as file:
            json.dump(data, file, indent=4)

    @classmethod
    def create_new_trace(cls, gameid: str):
        data = cls.get_json()

        data[gameid] = {
                            "300s": [0, 0, 0, 0],
                            "420s": [0, 0, 0, 0],
                            "540s": [0, 0, 0, 0],
                            "result": ["", 0, "00:00"]
                        }
                    
        cls.put_to_json(data=data)
        cls.tracing_game = gameid

    @classmethod
    def add_tracing(cls, timestamp, score):

        data = cls.get_json()
        data[cls.tracing_game][timestamp] = [
            score["blue_kills"],
            score["red_kills"],
            score["blue_towers"],
            score["red_towers"]
        ]
        cls.put_to_json(data=data)
        Validator.tracer[timestamp] = True

    @classmethod
    def complete_trace(cls, team, kills, timestamp):
        data = cls.get_json()
        data[cls.tracing_game]["result"] = [team, kills, timestamp]
        cls.put_to_json(data)
        cls.tracing_game = ''
        Validator.tracer["300s"] = False
        Validator.tracer["420s"] = False
        Validator.tracer["540s"] = False