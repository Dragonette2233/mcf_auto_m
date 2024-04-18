import json
import os
from mcf_data import SCORE_TRACE_PATH
from global_data import Validator, StatsRate

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
            'income': [
                        '00000', # blue_roles
                        '00000', # red_roles
                        0, # blue_kills
                        0, # red_kills
                        0, # blue_towers
                        0, # red_towers
                        0, # blue_gold
                        0, # red_gold
                        0, # blue_t1_hp
                        0, # red_t1_hp
                        0, # time
                    ],
            'result': []
        }
                    
        cls.put_to_json(data=data)
        cls.tracing_game = gameid

    @classmethod
    def add_tracing(cls, score):
        
        data = cls.get_json()
        data[cls.tracing_game]['income'] = [
            StatsRate.blue_roles,
            StatsRate.red_roles,
            score["blue_kills"],
            score["red_kills"],
            score["blue_towers"],
            score["red_towers"],
            score["blue_gold"],
            score["red_gold"],
            score["blue_t1_hp"],
            score["red_t1_hp"],
            score["time"]
        ]
        cls.put_to_json(data=data)
        Validator.tracer = True

    @classmethod
    def complete_trace(cls, team, kills, timestamp):
        data = cls.get_json()
        data[cls.tracing_game]["result"] = [team, kills, timestamp]
        cls.put_to_json(data)
        cls.tracing_game = ''
        Validator.tracer = False

    @classmethod
    def trace_predicts(cls):
        ...