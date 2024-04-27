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
    KTT_FULL_IDX = 12.8

    KTT_TW_HALF = 4.8
    KTT_TW_MIDDLE = 12

class PR:

    sc = None

    gtime = 0
    all_kills = 0
    module_kills = 0
    module_gold = 0
    gold_equals = 0

    income_ktt_idx = 0
    wretched_tower = 0
    towers_idx = 0 

    @classmethod
    def prepare_predict_values(cls):

        cls.gtime = cls.sc['time']
        cls.all_kills = cls.sc['blue_kills'] + cls.sc['red_kills']
        cls.module_kills = abs(cls.sc['blue_kills'] - cls.sc['red_kills'])
        cls.module_gold = abs(cls.sc['blue_gold'] - cls.sc['red_gold'])
        cls.gold_equals = cls.module_gold < 1.5

        cls.income_ktt_idx = ( 1200 - cls.gtime ) / ( 95 - cls.all_kills )
        cls.wretched_tower = min(cls.sc['blue_t1_hp'], cls.sc['red_t1_hp'])
        cls.towers_idx = ( 660 - cls.gtime ) / ( 0.1 + cls.wretched_tower)
    
    @classmethod
    def ktt_straigh_leader(cls):

        # kills coeff 0.52 | gold coeff 0.9
        blue_kills_lead = cls.sc['blue_kills'] > cls.sc['red_kills'] and cls.sc['red_kills'] / cls.sc['blue_kills'] < 0.52
        red_kills_lead = cls.sc['red_kills'] > cls.sc['blue_kills'] and cls.sc['blue_kills'] / cls.sc['red_kills'] < 0.52

        blue_gold_lead = cls.sc['blue_gold'] > cls.sc['red_gold'] and cls.sc['red_gold'] / cls.sc['blue_gold'] < 0.9
        red_gold_lead = cls.sc['red_gold'] > cls.sc['blue_gold'] and cls.sc['red_gold'] / cls.sc['blue_gold'] < 0.9

        blue_towers_lead = cls.sc['blue_t1_hp'] > 45 and cls.sc['red_t1_hp'] < 30
        red_towers_lead = cls.sc['red_t1_hp'] > 45 and cls.sc['blue_t1_hp'] < 30

        blue_leader = blue_kills_lead and blue_gold_lead and blue_towers_lead
        red_leader = red_kills_lead and red_gold_lead and red_towers_lead

        return blue_leader or red_leader
    
    @classmethod
    def kills_gold_equals(cls, kills, gold):

        return cls.all_kills > kills and cls.module_kills < 7 and cls.module_gold < gold

    @classmethod
    def two_towers_destroyed(cls, one_side=False, some_side=False, equals=False):

        if some_side:
            return cls.sc['blue_towers'] > 1 or cls.sc['red_towers'] > 1
        
        if one_side:
            blue_leader = cls.sc['blue_towers'] > 1 and cls.sc['red_towers'] == 0
            red_leader = cls.sc['red_towers'] > 1 and cls.sc['blue_towers'] == 0
            return blue_leader or red_leader

        if equals:
            return cls.sc['blue_towers'] == 1 and cls.sc['red_towers'] == 1

        return cls.sc['blue_towers'] + cls.sc['red_towers'] > 1

    @classmethod
    def towers_hp_more_than(cls, hp: int):

        return cls.sc['blue_t1_hp'] > hp and cls.sc['red_t1_hp'] > hp
    
    @classmethod
    def towers_hp_less_than(cls, hp: int):

        return cls.sc['blue_t1_hp'] < hp or cls.sc['red_t1_hp'] < hp

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

        match fl:
            case 'half':
                if cls.income_ktt_idx < PRstatic.KTT_T_HALF_IDX and cls.towers_idx >= PRstatic.KTT_TW_HALF: # >= 4.8
                    return True
                
                if cls.income_ktt_idx < PRstatic.KTT_HALF_IDX:
                    return True
            
            case 'middle':
                if cls.income_ktt_idx < PRstatic.KTT_MIDDLE_IDX and cls.towers_idx >= PRstatic.KTT_TW_MIDDLE:
                    return True
                
            case 'full':
                if cls.income_ktt_idx < PRstatic.KTT_FULL_IDX and cls.ktt_straigh_leader():
                    return True
                ...

    @classmethod
    def gen_main_predict(cls):

        predictions = {

                TelegramStr.tb_predict_half: [
                    (cls.kills_gold_equals(kills=60, gold=1.2) and cls.towers_hp_more_than(hp=50) and cls.gtime < 480 and CF.SR.tanks_in_teams()),
                    (cls.kills_gold_equals(kills=80, gold=1.2) and cls.two_towers_destroyed(equals=True) and cls.gtime < 540 and CF.SR.tanks_in_teams()),
                ],
                
                TelegramStr.tl_predict_full: [    
                    (cls.gtime > 249 and cls.ktt_tl(fl='full')),
                ],
                TelegramStr.tl_predict_middle: [   
                    (cls.gtime > 249 and cls.ktt_tl(fl='middle')),                 
                ],
                TelegramStr.tl_predict_half: [
                    (cls.gtime > 249 and cls.ktt_tl(fl='half')),
       
                    # Optional predicts
                    (cls.all_kills <= 30 and cls.module_kills >= 15 and cls.gtime > 420),
                    (cls.all_kills <= 38 and cls.module_kills >= 20 and cls.gtime > 420),
                    (cls.all_kills < 18 and cls.towers_hp_less_than(15) and cls.module_gold > 0.6 and cls.gtime > 240),
                    (cls.all_kills < 31 and cls.towers_hp_less_than(5) and cls.module_gold > 3.0 and cls.gtime > 380),
                    
                    (cls.all_kills < 38 and cls.two_towers_destroyed() and cls.gtime > 480),
                    (cls.all_kills < 55 and cls.two_towers_destroyed(one_side=True)),
                    (cls.all_kills < 50 and cls.two_towers_destroyed(some_side=True)),
                    

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