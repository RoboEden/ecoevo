class EnvConfig:
    player_num = 128
    total_step = 1000
    trade_radius = 4
    visual_radius = 7
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


class MapSize:
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