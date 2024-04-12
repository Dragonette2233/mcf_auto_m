import copy
from mcf_data import (
    StatsRate as SR,
)
from global_data import Validator

class Intense:

    time_targets = {
        'early_1': range(240, 300),
        'early_2': range(300, 360),
        'middle_1': range(360, 420),
        'middle_2': range(420, 480)
    }


class PR:

    score = None

    gtime = 0
    all_kills = 0
    module_kills = 0
    module_gold = 0
    gold_equals = 0

    @classmethod
    def prepare_predict_values(cls):

        cls.gtime = cls.score['time']
        cls.all_kills = cls.score['blue_kills'] + cls.score['red_kills']
        cls.module_kills = abs(cls.score['blue_kills'] - cls.score['red_kills'])
        cls.module_gold = abs(cls.score['blue_gold'] - cls.score['red_gold'])
        cls.gold_equals = cls.module_gold < 1.5

    @classmethod
    def straigh_leader(cls, gold_value, towers_hp: tuple):

        blue_gold_winner = cls.score['blue_gold'] > cls.score['red_gold'] and cls.module_gold > gold_value
        red_gold_winner = cls.score['red_gold'] > cls.score['blue_gold'] and cls.module_gold > gold_value

        blue_leader = cls.score['blue_t1_hp'] > towers_hp[0] and cls.score['red_t1_hp'] < towers_hp[1] and blue_gold_winner
        red_leader = cls.score['red_t1_hp'] > towers_hp[0] and cls.score['blue_t1_hp'] < towers_hp[1] and red_gold_winner
        
        return blue_leader or red_leader
    
    @classmethod
    def kills_gold_equals(cls, kills, gold):

        return cls.all_kills > kills and cls.module_kills < 7 and cls.module_gold < gold

    @classmethod
    def two_towers_destroyed(cls, one_side=False, some_side=False, equals=False):

        if some_side:
            return cls.score['blue_towers'] > 1 or cls.score['red_towers'] > 1
        
        if one_side:
            blue_leader = cls.score['blue_towers'] > 1 and cls.score['red_towers'] == 0
            red_leader = cls.score['red_towers'] > 1 and cls.score['blue_towers'] == 0
            return blue_leader or red_leader

        if equals:
            return cls.score['blue_towers'] == 1 and cls.score['red_towers'] == 1

        return cls.score['blue_towers'] + cls.score['red_towers'] > 1

    @classmethod
    def towers_hp_more_than(cls, hp: int):

        return cls.score['blue_t1_hp'] > hp and cls.score['red_t1_hp'] > hp
    
    @classmethod
    def towers_hp_less_than(cls, hp: int):

        return cls.score['blue_t1_hp'] < hp or cls.score['red_t1_hp'] < hp

    @classmethod
    def predict_possible(cls, predictions: dict, key: str):

        for mess, pr in predictions.items():
            for i, p in enumerate(pr):
                if p:
                    return (mess, key, i)
        # else:
        return (None, None, None)
    
    @classmethod
    def gen_predict(cls, score):

        possible_predicts = []

        cls.score = copy.deepcopy(score)
        cls.prepare_predict_values()

        if not Validator.predict_value_flet['stats']:

            spredictions = {
                '🔽S_PR 110.5М FL_1🔽': [
                    (SR.tl_accepted() and cls.all_kills < 30 and cls.towers_hp_less_than(hp=25) and cls.gtime > 400),
                ],
                '🔽S_PR 110.5М FL_0.5🔽': [
                    (SR.tl_accepted() and cls.all_kills < 24 and cls.gtime > 400)
                ],
                '🔼S_PR 110.5Б FL_0.5🔼': [
                    (SR.tb_accepted() and cls.kills_gold_equals(kills=45, gold=1.5) and cls.gtime < 360),
                    (SR.tb_accepted() and SR.tanks_in_teams())
                ]
            }

            possible_predicts.append(cls.predict_possible(predictions=spredictions, key='stats'))
        
        else:
            possible_predicts.append((None, None, None))

        if not Validator.predict_value_flet['main']:
            
            predictions = {
                '🔼PR 110.5Б FL_1🔼': [
                    (cls.kills_gold_equals(kills=60, gold=1.2) and cls.towers_hp_more_than(hp=65) and cls.gtime < 480 and SR.tanks_in_teams()),
                    (cls.kills_gold_equals(kills=80, gold=1.2) and cls.two_towers_destroyed(equals=True) and cls.gtime < 540 and SR.tanks_in_teams()),

                ],
                '🔼PR 110.5Б FL_0.5🔼': [
                    (cls.kills_gold_equals(kills=50, gold=1.5) and cls.towers_hp_more_than(hp=65) and cls.gtime < 540 and SR.tanks_in_teams(one_side=True)),
                    (cls.kills_gold_equals(kills=46, gold=1.3) and cls.towers_hp_more_than(hp=70) and cls.gtime < 420 and SR.tanks_in_teams(one_side=True)),
                    (cls.kills_gold_equals(kills=40, gold=1.0) and cls.towers_hp_more_than(hp=75) and cls.gtime < 420 and SR.tanks_in_teams(one_side=True)),
                    (cls.kills_gold_equals(kills=36, gold=0.8) and cls.towers_hp_more_than(hp=80) and cls.gtime < 360 and SR.tanks_in_teams(one_side=True)),
                ],

                '🔽PR 110.5М FL_1🔽': [

                    (cls.all_kills < 18 and cls.straigh_leader(gold_value=2.0, towers_hp=(75, 35)) and cls.gtime > 240),
                    (cls.all_kills < 24 and cls.straigh_leader(gold_value=2.3, towers_hp=(65, 30)) and cls.gtime > 300),
                    (cls.all_kills < 30 and cls.straigh_leader(gold_value=2.6, towers_hp=(60, 25)) and cls.gtime > 360),
                    (cls.all_kills < 36 and cls.straigh_leader(gold_value=2.9, towers_hp=(55, 20)) and cls.gtime > 420),
                    (cls.all_kills < 42 and cls.straigh_leader(gold_value=3.2, towers_hp=(50, 15)) and cls.gtime > 540),
                    (cls.all_kills < 50 and cls.straigh_leader(gold_value=3.5, towers_hp=(45, 10)) and cls.module_kills > 13 and cls.gtime > 540)

                    # Optional predicts
                    (cls.all_kills < 39 and cls.straigh_leader(gold_value=0.8, towers_hp=(80, 10)) and cls.gtime > 400)
                    
                ],
                '🔽PR 110.5М FL_0.75🔽': [

                    (cls.all_kills < 14 and cls.towers_hp_less_than(35) and cls.gtime > 240),
                    (cls.all_kills < 20 and cls.towers_hp_less_than(30) and cls.gtime > 300),
                    (cls.all_kills < 26 and cls.towers_hp_less_than(25) and cls.gtime > 360),
                    (cls.all_kills < 32 and cls.towers_hp_less_than(20) and cls.gtime > 420),
                    (cls.all_kills < 38 and cls.towers_hp_less_than(15) and cls.gtime > 480),

                    (cls.all_kills < 38 and cls.two_towers_destroyed() and cls.gtime > 480),
                    (cls.all_kills < 55 and cls.two_towers_destroyed(one_side=True)),
                    (cls.all_kills < 50 and cls.two_towers_destroyed(some_side=True)),

                    # Optional predicts
                    (cls.all_kills < 25 and cls.straigh_leader(gold_value=2.8, towers_hp=(70, 0)) and cls.gtime > 240),

                    
                ],
                '🔽PR 110.5М FL_0.5🔽': [
                    
                    (cls.all_kills < 10 and cls.towers_hp_less_than(90) and cls.gtime > 240),
                    (cls.all_kills < 16 and cls.towers_hp_less_than(85) and cls.gtime > 300),
                    (cls.all_kills < 20 and cls.towers_hp_less_than(80) and cls.gtime > 360),
                    (cls.all_kills < 22 and cls.towers_hp_less_than(75) and cls.gtime > 420),
                    (cls.all_kills < 28 and cls.towers_hp_less_than(70) and cls.gtime > 480),


                    (cls.all_kills < 7 and cls.gtime > 240),
                    (cls.all_kills < 10 and cls.gtime > 300),
                    (cls.all_kills < 13 and cls.gtime > 360),
                    (cls.all_kills < 16 and cls.gtime > 420),
                    (cls.all_kills < 19 and cls.gtime > 480),

                    (cls.all_kills <= 30 and cls.module_kills >= 15 and cls.gtime > 420),
                    (cls.all_kills <= 38 and cls.module_kills >= 20 and cls.gtime > 420),

                    # Optional predicts
                    (cls.all_kills < 18 and cls.towers_hp_less_than(15) and cls.module_gold > 0.6 and cls.gtime > 240),
                    (cls.all_kills < 31 and cls.towers_hp_less_than(5) and cls.module_gold > 3.0 and cls.gtime > 380)
                    

                ]

            }

            possible_predicts.append(cls.predict_possible(predictions=predictions, key='main'))

        else:
            possible_predicts.append((None, None, None))


        return possible_predicts