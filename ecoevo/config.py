class EnvConfig:
    player_num = 100
    total_step: 10000
    name = [
        'pepper_bro',
    ]


class MapSize:
    width = 32
    height = 32


class PlayerConfig:
    max_health = 100
    comsumption_per_step = 1


class RewardConfig:
    threshold = 0
    w = 0.1
    penalty = 10
    rho = 0.5