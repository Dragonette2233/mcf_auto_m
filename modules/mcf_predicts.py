from dynamic_data import CF
from static_data import TelegramStr

class Intense:

    time_targets = {
        'early_1': range(240, 300),
        'early_2': range(300, 360),
        'middle_1': range(360, 420),
        'middle_2': range(420, 480)
    }

class PRstatic:
    KTT_HALF_IDX = 10.9
    KTT_T_HALF_IDX = 11.5
    KTT_MIDDLE_IDX = 12.1
    KTT_FULL_IDX = ...
    # KTT_KILLS_2 = 0.057
    # KTT_TOWERS_1 = 0.06
    # TW_HP = ...

# class PredictsConstants:

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

        blue_kills_lead = cls.score['blue_kills'] > cls.score['red_kills'] and cls.module_kills > 5
        red_kills_lead = cls.score['red_kills'] > cls.score['blue_kills'] and cls.module_kills > 5

        blue_gold_lead = cls.score['blue_gold'] > cls.score['red_gold'] and cls.module_gold > gold_value
        red_gold_lead = cls.score['red_gold'] > cls.score['blue_gold'] and cls.module_gold > gold_value

        blue_towers_lead = cls.score['blue_t1_hp'] > towers_hp[0] and cls.score['red_t1_hp'] < towers_hp[1]#  and blue_gold_winner
        red_towers_lead = cls.score['red_t1_hp'] > towers_hp[0] and cls.score['blue_t1_hp'] < towers_hp[1]#  and red_gold_winner

        blue_leader = blue_kills_lead and blue_gold_lead and blue_towers_lead
        red_leader = red_kills_lead and red_gold_lead and red_towers_lead

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
    def ktt_tl(cls, fl='half'):

        income_idx = ( 1200 - cls.gtime ) / ( 95 - cls.all_kills )
        wretchet_tower = min(cls.score['blue_t1_hp'], cls.score['red_t1_hp'])
    
        match fl:
            case 'half':
                if income_idx < PRstatic.KTT_HALF_IDX:
                    return True
            case 'half_towers':
                towers_idx = ( 100 - wretchet_tower ) / cls.gtime
                if income_idx < PRstatic.KTT_T_HALF_IDX and towers_idx >= 0.06:
                    return True
            case 'middle_towers':
                towers_idx = ( 660 - cls.gtime ) / ( 0.1 + wretchet_tower)
                if income_idx < PRstatic.KTT_MIDDLE_IDX and towers_idx >= 12:
                    return True
            case _:
                ...

    @classmethod
    def gen_main_predict(cls):

        predictions = {

                TelegramStr.tb_predict_half: [
                    (cls.kills_gold_equals(kills=60, gold=1.2) and cls.towers_hp_more_than(hp=50) and cls.gtime < 480 and CF.SR.tanks_in_teams()),
                    (cls.kills_gold_equals(kills=80, gold=1.2) and cls.two_towers_destroyed(equals=True) and cls.gtime < 540 and CF.SR.tanks_in_teams()),

                ],
                
                TelegramStr.tl_predict_full: [

                    (cls.all_kills < 16 and cls.straigh_leader(gold_value=2.0, towers_hp=(75, 30)) and cls.gtime > 250),
                    (cls.all_kills < 22 and cls.straigh_leader(gold_value=2.0, towers_hp=(65, 25)) and cls.gtime > 310),
                    (cls.all_kills < 28 and cls.straigh_leader(gold_value=2.2, towers_hp=(60, 20)) and cls.gtime > 360),
                    (cls.all_kills < 33 and cls.straigh_leader(gold_value=2.2, towers_hp=(55, 15)) and cls.gtime > 420),
                    (cls.all_kills < 42 and cls.straigh_leader(gold_value=2.5, towers_hp=(50, 10)) and cls.gtime > 540),
                    (cls.all_kills < 50 and cls.straigh_leader(gold_value=2.5, towers_hp=(45, 5)) and cls.module_kills > 13 and cls.gtime > 540),

                    # Optional predicts
                    # (cls.all_kills < 39 and cls.straigh_leader(gold_value=0.8, towers_hp=(80, 10)) and cls.gtime > 400),
                    
                ],
                TelegramStr.tl_predict_middle: [
                    
                    (cls.gtime > 249 and cls.ktt_tl(fl='middle_towers')),

                    # deprecated predicts
                    # (cls.all_kills < 14 and cls.towers_hp_less_than(30) and cls.gtime > 250), # 25 cf
                    # (cls.all_kills < 20 and cls.towers_hp_less_than(25) and cls.gtime > 310),
                    # (cls.all_kills < 26 and cls.towers_hp_less_than(20) and cls.gtime > 360),
                    # (cls.all_kills < 32 and cls.towers_hp_less_than(15) and cls.gtime > 420),
                    # (cls.all_kills < 38 and cls.towers_hp_less_than(10) and cls.gtime > 480),

                    # Optional predicts
                    (cls.all_kills < 25 and cls.straigh_leader(gold_value=2.8, towers_hp=(70, 0)) and cls.gtime > 240),
                    (cls.all_kills < 38 and cls.two_towers_destroyed() and cls.gtime > 480),
                    (cls.all_kills < 55 and cls.two_towers_destroyed(one_side=True)),
                    (cls.all_kills < 50 and cls.two_towers_destroyed(some_side=True)),

                    
                ],
                TelegramStr.tl_predict_half: [
                    
                    # KTT predicts
                    (cls.gtime > 249 and cls.ktt_tl(fl='half_towers')),
                    (cls.gtime > 249 and cls.ktt_tl(fl='half')),
                    
                    # deprecated predicts
                    # (cls.all_kills < 11 and cls.towers_hp_less_than(90) and cls.gtime > 250), # 43 cf ## 42
                    # (cls.all_kills < 17 and cls.towers_hp_less_than(85) and cls.gtime > 310), ## 44
                    # (cls.all_kills < 21 and cls.towers_hp_less_than(80) and cls.gtime > 370), ## 46
                    # (cls.all_kills < 26 and cls.towers_hp_less_than(75) and cls.gtime > 420), ## 47
                    # (cls.all_kills < 31 and cls.towers_hp_less_than(70) and cls.gtime > 480), ## 49

                    
                    # Optional predicts
                    (cls.all_kills <= 30 and cls.module_kills >= 15 and cls.gtime > 420),
                    (cls.all_kills <= 38 and cls.module_kills >= 20 and cls.gtime > 420),
                    (cls.all_kills < 18 and cls.towers_hp_less_than(15) and cls.module_gold > 0.6 and cls.gtime > 240),
                    (cls.all_kills < 31 and cls.towers_hp_less_than(5) and cls.module_gold > 3.0 and cls.gtime > 380),
                    

                ]

            }

        return cls.predict_possible(predictions=predictions, key='main')

    @classmethod
    def gen_stats_predict(cls):

        spredictions = {
                TelegramStr.tl_spredict_half: [
                    
                    (CF.SR.tl_accepted() and cls.all_kills < 30 and cls.towers_hp_less_than(hp=25) and cls.gtime > 400),
                    (CF.SR.tl_accepted() and cls.all_kills < 24 and cls.gtime > 400),
                    (CF.SR.tl_accepted() and cls.all_kills < 35 and CF.SR.tanks_in_teams(both_excluded=True) and cls.gtime > 400)
                ],
                TelegramStr.tb_spredict_half: [
                    (CF.SR.tb_accepted() and cls.kills_gold_equals(kills=45, gold=1.5) and cls.gtime < 480),
                    (CF.SR.tb_accepted() and cls.kills_gold_equals(kills=30, gold=1.5) and CF.SR.tanks_in_teams() and cls.gtime < 400),
                ]
            }

        return cls.predict_possible(predictions=spredictions, key='stats')
    

# PR.ktt_corr_index