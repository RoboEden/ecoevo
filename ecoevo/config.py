class EnvConfig:
    player_num = 128
    total_step = 1000
    trade_radius = 4
    visual_radius = 7
    personae = [
        'gold_digger',
        'hazelnut_farmer',
        'coral_collector',
        'sand_picker',
        'pineapple_farmer',
        'peanut_farmer',
        'stone_picker',
        'pumpkin_farmer',
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
    weight_coef = 0.1
    penalty = 10
    rho = 0.5