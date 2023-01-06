import pathlib


class EnvConfig:
    total_step = 1000
    trade_radius = 4
    visual_radius = 7
    num_person_type = 8
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
    comsumption_per_step = 10


class RewardConfig:
    threshold = 0
    weight_coef = 0
    penalty = 0


class DataPath:
    item_yaml = pathlib.Path(__file__).parent / "data" / "items.yaml"
    player_yaml = pathlib.Path(__file__).parent / "data" / "player.yaml"
    map_json = pathlib.Path(__file__).parent / "data" / "base.json"
