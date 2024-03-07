import json

with open('trace.json', 'r', encoding='utf-8') as file:
    data: dict = json.load(file)


def calculate_leader(value: dict):
    blue_leader_start = value['300s'][0] > value['300s'][1]
    blue_leader_next = value['420s'][0] > value['420s'][1]
    blue_leader_end = value['540s'][0] > value['540s'][1]

    red_leader_start = value['300s'][1] > value['300s'][0]
    red_leader_next = value['420s'][1] > value['420s'][0]
    red_leader_end = value['540s'][1] > value['540s'][0]

    blue_leader = blue_leader_start and blue_leader_next and blue_leader_end
    red_leader = red_leader_start and red_leader_next and red_leader_end

    return blue_leader or red_leader

for key, value in data.items():
    if all([value['300s'][0] != 0, value['420s'][0] != 0, value['540s'][0] != 0]):
        started_total = value['300s'][0] + value['300s'][1]
        started_towers = value['300s'][2] + value['300s'][3]
        straight_leader = calculate_leader(value)
        first_intense = sum(value['420s'][0:2]) - sum(value['300s'][0:2])
        seconds_intense = sum(value['540s'][0:2]) - sum(value['420s'][0:2])
        first_towers = sum(value['420s'][2:4])
        seconds_towers = sum(value['540s'][2:4])
        result = value['result'][1]
        if first_intense > 10 and seconds_intense > 10 and started_total > 23 and straight_leader and seconds_towers == 1:
            print(f'Start: {started_total} TW: {started_towers} | I_1: {first_intense} TW: {first_towers} | I_2: {seconds_intense} TW: {seconds_towers} | RES: {result}')
