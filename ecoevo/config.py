class EnvConfig:
    player_num = 100
    total_step: 10000
    trade_radius = 4
    visual_radius = 7
    name = [
        'pepper_bro',
    ]
    bag_volume = 100


class MapSize:
    width = 32
    height = 32


class PlayerConfig:
    max_health = 100
    comsumption_per_step = 1


class RewardConfig:
    threshold = 0
    weight_coef = 0.1
    penalty = 10
    rho = 0.5