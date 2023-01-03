import pathlib


class EnvConfig:
    total_step = 1000
    trade_radius = 4
    visual_radius = 7
    num_person_type = 16
    personae = [
        *(['gold_digger'] * num_person_type),
        *(['hazelnut_farmer'] * num_person_type),
        *(['coral_collector'] * num_person_type),
        *(['sand_picker'] * num_person_type),
        *(['pineapple_farmer'] * num_person_type),
        *(['peanut_farmer'] * num_person_type),
        *(['stone_picker'] * num_person_type),
        *(['pumpkin_farmer'] * num_person_type),
    ]


class MapConfig:
    width = 32
    height = 32


class PlayerConfig:
    bag_volume = 10 ** 8
    max_health = 100
    comsumption_per_step = 1


class RewardConfig:
    threshold = 0
    weight_coef = 0
    penalty = 1
    
    # dis for disposable, dur for durable; nec for necessity, lux for luxury
    alpha_nec, alpha_lux = 0.53, 0.3
    rho_nec, rho_lux = 0.2, 0.3
    eta_dis_nec, eta_dis_lux = 0.53, 0.87
    lambda_nec, lambda_lux = 48, 46
    eta_dur_nec, eta_dur_lux = 0.1, 0.16
    c_dis_nec, c_dis_lux, c_dur_nec, c_dur_lux = 3.58, 3.98, 100, 100


class DataPath:
    item_yaml = pathlib.Path(__file__).parent / "entities" / "items.yaml"
    player_yaml = pathlib.Path(__file__).parent / "entities" / "player.yaml"
    map_json = pathlib.Path(__file__).parent / "maps" / "data" / "base.json"
