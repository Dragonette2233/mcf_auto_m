from dynamic_data import CF
from static_data import TelegramStr

class PRstatic:

    KTT_HALF_IDX = 10.9
    KTT_T_HALF_IDX = 11.5
    KTT_MIDDLE_IDX = 11.9
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

    tl_ktt_idx = 0
    wretched_tower = 0
    towers_idx = 0 

    @classmethod
    def prepare_predict_values(cls):

        cls.gtime = cls.sc['time']
        cls.all_kills = cls.sc['blue_kills'] + cls.sc['red_kills']
        cls.module_kills = abs(cls.sc['blue_kills'] - cls.sc['red_kills'])
        cls.module_gold = abs(cls.sc['blue_gold'] - cls.sc['red_gold'])
        cls.gold_equals = cls.module_gold < 1.5

        cls.tl_ktt_idx = ( 1200 - cls.gtime ) / ( 95 - cls.all_kills )
        cls.tb_ktt_idx = ( 1000 + cls.gtime ) / ( 120 + cls.all_kills )
        cls.wretched_tower = min(cls.sc['blue_t1_hp'], cls.sc['red_t1_hp'])

        cls.towers_idx = ( 660 - cls.gtime ) / ( 0.1 + cls.wretched_tower)

        if cls.sc['blue_towers'] < 2 and cls.sc['red_towers'] < 2:
            cls.tb_towers_idx = ( 900 - cls.gtime ) / ( 100 + cls.wretched_tower)
        else:
            cls.tb_towers_idx = 4

        cls.module_kills_idx = min(cls.sc['blue_kills'], cls.sc['red_kills']) / (max(cls.sc['blue_kills'], cls.sc['red_kills']) + 0.01)

    @classmethod
    def ktt_straigh_leader(cls):

        blue_kills_lead = cls.sc['blue_kills'] > cls.sc['red_kills'] and cls.sc['red_kills'] / cls.sc['blue_kills'] < 0.52
        red_kills_lead = cls.sc['red_kills'] > cls.sc['blue_kills'] and cls.sc['blue_kills'] / cls.sc['red_kills'] < 0.52

        blue_gold_lead = cls.sc['blue_gold'] > cls.sc['red_gold'] and cls.sc['red_gold'] / cls.sc['blue_gold'] < 0.9
        red_gold_lead = cls.sc['red_gold'] > cls.sc['blue_gold'] and cls.sc['blue_gold'] / cls.sc['red_gold'] < 0.9

        blue_towers_lead = cls.sc['blue_t1_hp'] > 45 and cls.sc['red_t1_hp'] < 30
        red_towers_lead = cls.sc['red_t1_hp'] > 45 and cls.sc['blue_t1_hp'] < 30

        blue_leader = blue_kills_lead and blue_gold_lead and blue_towers_lead
        red_leader = red_kills_lead and red_gold_lead and red_towers_lead

        return blue_leader or red_leader
    
    @classmethod
    def gold_not_equals(cls):
        return abs(cls.sc['blue_gold'] - cls.sc['red_gold']) > 1.3

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
    def ktt_tb(cls, fl):
        match fl:
            case 'half':
                if cls.tb_ktt_idx <= 8.45 and cls.tb_towers_idx <= 3.6 and cls.module_kills_idx >= 0.75:
                    return True
            case 's_half':
                if cls.tb_ktt_idx <= 8.8 and cls.tb_towers_idx <= 3.9 and cls.module_kills_idx >= 0.7:
                    return True
        
    @classmethod
    def ktt_tl(cls, fl='half'):
        match fl:
            case 'half':
                
                if any([
                    cls.tl_ktt_idx < PRstatic.KTT_T_HALF_IDX and cls.towers_idx >= PRstatic.KTT_TW_HALF,
                    cls.tl_ktt_idx < PRstatic.KTT_HALF_IDX
                ]):
                    return True
            case 's_half':
                if any([
                    cls.tl_ktt_idx < PRstatic.KTT_MIDDLE_IDX,
                    cls.tl_ktt_idx < PRstatic.KTT_FULL_IDX and cls.towers_idx >= PRstatic.KTT_TW_HALF,
                ]):
                    return True
            case 'middle':
                if cls.tl_ktt_idx < PRstatic.KTT_MIDDLE_IDX and cls.towers_idx >= PRstatic.KTT_TW_MIDDLE:
                    return True
                
            case 'full':
                if cls.tl_ktt_idx < PRstatic.KTT_FULL_IDX and cls.ktt_straigh_leader():
                    return True
            case _:
                ...


    @classmethod
    def gen_main_predict(cls):

        predictions = {

                TelegramStr.tb_predict_half: [
                    (cls.gtime > 360 and cls.ktt_tb(fl='half')),
                    (cls.gtime > 400 and cls.ktt_tb(fl="s_half") and CF.SR.tb_accepted()),
                ],
                
                TelegramStr.tl_predict_full: [    
                    (cls.gtime > 239 and cls.ktt_tl(fl='full')),
                ],
                TelegramStr.tl_predict_middle: [   
                    (cls.gtime > 239 and cls.ktt_tl(fl='middle')),
                ],
                TelegramStr.tl_predict_half: [
                    (cls.gtime > 239 and cls.ktt_tl(fl='half')),
                    (cls.gtime > 300 and cls.ktt_tl(fl="s_half") and CF.SR.tl_accepted()),
       
                    # Optional predicts
                    (cls.all_kills <= 30 and cls.module_kills >= 15 and cls.gtime > 420),
                    (cls.all_kills <= 38 and cls.module_kills >= 20 and cls.gtime > 420),
                    
                    (cls.all_kills < 38 and cls.two_towers_destroyed() and cls.gtime > 480),
                    (cls.all_kills < 48 and cls.two_towers_destroyed(one_side=True)),
                    (cls.all_kills < 35 and cls.two_towers_destroyed(some_side=True)),
                    

                ]

            }

        for mess, pr in predictions.items():
            for i, p in enumerate(pr):
                if p:
                    return (mess, i)
                
        return False