class EnvConfig:
    player_num = 100
    player_ids = list(range(player_num))
    total_step = 10000
    trade_radius = 400
    visual_radius = 7
    personae = [
        *(['pepper_bro'] * 14),
        *(['coral_hunter'] * 14),
        *(['sand_collector'] * 14),
        *(['pineapple_farmer'] * 14),
        *(['peanut_collector'] * 14),
        *(['stone_picker'] * 14),
        *(['pumpkin_farmer'] * 16),
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