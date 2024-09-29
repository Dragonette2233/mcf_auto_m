from static import (
    TEN_ROLES_DICT,
    STATS_BASE_ITERATOR
)

def get_aram_statistic(blue_entry: list, red_entry: list):

    def _rate_chance_and_color(income_value, divider):
        '''
            divider: count of all games
            income_value: count of wins or totals
            out_value: float represent of winrate or total rate

        '''
        out_value = income_value / divider * 100

        match out_value, divider:
            case 100.0, div:
                return ['100%', '🟩']
            case 0, div:
                return ['0%', '🟥']
            case out, div if div < 10:
                if out >= 80: return [f"{'%.1f' % out}%", '🟩']
                if out < 80: return [f"{'%.1f' % out}%", '🟥']
            case out, div if div in range(10, 15):
                if out >= 75: return [f"{'%.1f' % out}%", '🟩']
                if out < 75: return [f"{'%.1f' % out}%", '🟥']
            case out, div:
                if out >= 70: return [f"{'%.1f' % out}%", '🟩']
                if out < 70: return [f"{'%.1f' % out}%", '🟥']
            case _:
                return [f"{'%.1f' % out}%", '?']

    def _find_games_from_stats(teams: dict[str, int]):

        roles_strings = {
            'T1': ''.join(teams['T1']),
            'T2': ''.join(teams['T2'])
        }
        
        blue_string = '_'.join(roles_strings.values())
        red_string = '_'.join(reversed(roles_strings))

        target = None
        
        for match in STATS_BASE_ITERATOR:
            
            if match.startswith((blue_string, red_string)):
                target = (match, 'blue' if match.startswith(blue_string) else 'red')
                break
        else:
            return None
        
        leader = target[1]
        results = target[0].split('|')
        w1_rate = results[1] if leader == 'blue' else results[2]
        w2_rate = results[1] if leader == 'red' else results[2]

        return {
                'blue_roles': roles_strings['T1'],
                'red_roles': roles_strings['T2'],
                'w1': int(w1_rate),
                'w2': int(w2_rate),
                'tb': int(results[3]),
                'tl': int(results[4]),
                'all_m': int(results[5]),
                'all_ttl': int(results[6][:-1])
            }
    
    def _get_converted_roles(champ):
        
        for i in TEN_ROLES_DICT.items():
            if champ.lower().capitalize() in i[1]: 
                return i[0]
        
    teams = {
        'T1': blue_entry,
        'T2': red_entry,
    }

    """
        Getting list of roles by converting character name into role index
    """
    teams_by_ten_roles = {
        'T1': sorted([_get_converted_roles(char) for char in teams['T1']]),
        'T2': sorted([_get_converted_roles(char) for char in teams['T2']])
    }

    """
        Converting list of roles into string for comparing with items in .txt
    """
    
    ten_roles_rate = _find_games_from_stats(teams_by_ten_roles)
    
    if ten_roles_rate is None or ten_roles_rate['all_ttl'] < 6:

        final_result = {
            'blue_roles': ''.join(teams_by_ten_roles['T1']),
            'red_roles': ''.join(teams_by_ten_roles['T2']),
            'w1': 0,
            'w2': 0,
            'tb': 0,
            'tl': 0,
            'all_m': 0,
            'all_ttl': 0
        }

    else:
        final_result = {
            'blue_roles': ten_roles_rate['blue_roles'],
            'red_roles': ten_roles_rate['red_roles'],
            'w1': _rate_chance_and_color(int(ten_roles_rate['w1']), int(ten_roles_rate['all_m'])),
            'w2': _rate_chance_and_color(int(ten_roles_rate['w2']), int(ten_roles_rate['all_m'])),
            'tb': _rate_chance_and_color(int(ten_roles_rate['tb']), int(ten_roles_rate['all_ttl'])),
            'tl': _rate_chance_and_color(int(ten_roles_rate['tl']), int(ten_roles_rate['all_ttl'])),
            'all_m': ten_roles_rate['all_m'],
            'all_ttl': ten_roles_rate['all_ttl']
        }
        
    return final_result

    
