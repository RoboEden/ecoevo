import pathlib


class EnvConfig:
    total_step = 1000
    trade_radius = 2
    visual_radius = 4
    personae = [
        *(['gold_digger'] * 16),
        *(['hazelnut_farmer'] * 16),
        *(['coral_collector'] * 16),
        *(['sand_picker'] * 16),
        *(['pineapple_farmer'] * 16),
        *(['peanut_farmer'] * 16),
        *(['stone_picker'] * 16),
        *(['pumpkin_farmer'] * 16),
    ]
    bag_volume = 1000


class MapConfig:
    width = 32
    height = 32


class PlayerConfig:
    max_health = 100
    comsumption_per_step = 10


class RewardConfig:
    threshold = 0
    weight_coef = 0.0001
    penalty = 1
    rho = 0.5


class DataPath:
    item_yaml = pathlib.Path(__file__).parent / "entities" / "items.yaml"
    player_yaml = pathlib.Path(__file__).parent / "entities" / "player.yaml"
    map_json = pathlib.Path(__file__).parent / "maps" / "data" / "base.json"
