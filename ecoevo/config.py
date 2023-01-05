import pathlib


class EnvConfig:
    total_step = 1000
    trade_radius = 4
    visual_radius = 7
    num_person_type = 4
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
    bag_volume = 1e8
    max_health = 100
    comsumption_per_step = 5


class RewardConfig:
    threshold = 0
    weight_coef = 0
    penalty = 0.01

    # dis for disposable, dur for durable; nec for necessity, lux for luxury
    alpha_nec, alpha_lux = 0.62, 0.3
    rho_nec, rho_lux = 0.2, 0.3
    eta_dis_nec, eta_dis_lux = 0.53, 0.87
    lambda_nec, lambda_lux = 59, 41
    eta_dur_nec, eta_dur_lux = 0.1, 0.16
    c_dis_nec, c_dis_lux, c_dur_nec, c_dur_lux = 6.46, 5.05, 100, 100
    c_base = 429.293

    trade_reward = 0.1


class DataPath:
    item_yaml = pathlib.Path(__file__).parent / "data" / "items.yaml"
    player_yaml = pathlib.Path(__file__).parent / "data" / "player.yaml"
    map_json = pathlib.Path(__file__).parent / "data" / "base.json"
